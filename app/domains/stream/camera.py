import os
import threading
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from ultralytics import YOLO
from app.configs import REG_DIR

camera = None
camera_lock = threading.Lock()
ESP32_STREAM_URL = "http://192.168.137.159:81/stream"


model = YOLO("yolov8n.pt")
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
# 저사양 환경을 고려(320x320)
face_app.prepare(ctx_id=0, det_size=(320, 320))

# 3) 신원 데이터베이스 및 트래킹 변수
known_face_encodings = []
known_face_names = []
tracked_identities = {}  # {track_id: "이름"}


def init_camera():
    global camera

    if camera is None:
        camera = cv2.VideoCapture(ESP32_STREAM_URL)
        build_face_db()


def build_face_db():
    global known_face_encodings, known_face_names

    if not os.path.exists(REG_DIR):
        os.makedirs(REG_DIR)
        print(f"'{REG_DIR}'폴더가 없어 새로 생성되었습니다.")
        return

    for person_name in os.listdir(REG_DIR):
        person_dir = os.path.join(REG_DIR, person_name)

        if not os.path.isdir(person_dir):
            continue

        print(f"[{person_name}]의 사진들을 분석 중...")
        success_count = 0

        # 2단계: 각 사람 폴더 안의 이미지 파일 루프
        for filename in os.listdir(person_dir):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(person_dir, filename)
                img = cv2.imread(path)

                if img is None:
                    continue

                # InsightFace로 얼굴 분석
                faces = face_app.get(img)

                if len(faces) > 0:
                    # 얼굴 임베딩 데이터와 매칭될 '폴더명(이름)'을 저장
                    known_face_encodings.append(faces[0].normed_embedding)
                    known_face_names.append(
                        person_name
                    )  # 파일명이 아니라 폴더명을 이름으로 사용!
                    success_count += 1
                else:
                    print(f"  └ 실패 (얼굴 인식 불가): {filename}")

        if success_count > 0:
            print(f"  └ {person_name} 등록 완료 ({success_count}장의 사진)")

    print(
        f">> 총 {len(set(known_face_names))}명, {len(known_face_names)}개의 얼굴 DB 구축 완료.\n"
    )


def reconnect_camera():
    global camera

    try:
        if camera is not None:
            camera.release()

    except Exception as e:
        print(e)

    camera = cv2.VideoCapture(ESP32_STREAM_URL)
    print("camera reconnected")


def get_frame():
    global camera, tracked_identities
    if camera is None:
        return None

    try:
        if not camera.isOpened():
            reconnect_camera()
            return None

        with camera_lock:
            success, frame = camera.read()

        if not success:
            reconnect_camera()
            return None

        # ==========================================
        # 2. YOLO + ByteTrack 추적 파이프라인
        # ==========================================
        # persist=True 가 ByteTrack을 활성화하는 옵션입니다. 클래스는 사람(0)만 탐지합니다.
        results = model.track(frame, persist=True, classes=[0], conf=0.5, verbose=False)
        result = results[0]

        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.int().cpu().tolist()
            track_ids = result.boxes.id.int().cpu().tolist()
            confidences = result.boxes.conf.float().cpu().tolist()

            for box, track_id, conf in zip(boxes, track_ids, confidences):
                x1, y1, x2, y2 = box

                # 예외 처리: 바운딩 박스가 화면 밖으로 나가는 것 방지
                y1, y2 = max(0, y1), min(frame.shape[0], y2)
                x1, x2 = max(0, x1), min(frame.shape[1], x2)

                # [최적화] 처음 본 Track ID 일 때만 신원 분석(InsightFace) 수행
                if track_id not in tracked_identities:
                    tracked_identities[track_id] = "Unknown"  # 기본값 지정

                    # 사람 영역 크롭
                    person_crop = frame[y1:y2, x1:x2]

                    if person_crop.size > 0 and len(known_face_encodings) > 0:
                        # 크롭된 사람 영역 내부에서 얼굴 추출
                        faces = face_app.get(person_crop)

                        if len(faces) > 0:
                            current_embedding = faces[0].normed_embedding
                            best_match = "Unknown"
                            max_similarity = -1.0

                            # DB 내의 얼굴들과 코사인 유사도 비교
                            for known_embedding, name in zip(
                                known_face_encodings, known_face_names
                            ):
                                # 두 벡터의 내적 (정규화된 벡터이므로 내적이 곧 코사인 유사도)
                                similarity = np.dot(current_embedding, known_embedding)

                                if similarity > max_similarity:
                                    max_similarity = similarity
                                    best_match = name

                            # 유사도가 기준값(0.4)을 넘으면 신원 확정 (InsightFace 기준 보통 0.4~0.45가 적당)
                            if max_similarity > 0.42:
                                tracked_identities[track_id] = (
                                    f"{best_match} ({max_similarity * 100:.0f}%)"
                                )

                # ==========================================
                # 3. 화면 시각화 (인식 결과 그리기)
                # ==========================================
                identity_label = tracked_identities.get(track_id, "Unknown")

                # 등록된 사람(Unknown이 아님)은 초록색, 미등록자는 빨간색 상자
                color = (0, 255, 0) if "Unknown" not in identity_label else (0, 0, 255)

                # 박스 및 이름 표기
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    f"ID {track_id}: {identity_label}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

                # 중심점 표시
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.circle(frame, (center_x, center_y), 4, (255, 0, 0), -1)

        return frame

    except Exception as e:
        print("camera exception:", e)
        reconnect_camera()
        return None

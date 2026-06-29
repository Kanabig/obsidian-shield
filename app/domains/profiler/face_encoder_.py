import json
import os
import threading
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from ultralytics import YOLO
from app.configs import REG_DIR, ESP32_STREAM_URL
from app.utils.json_manager import FACES_ENCODINGS_FILE


class StreamCamera:
    """ESP32 스트림 카메라 연결 및 프레임 수급을 담당하는 클래스"""

    _threading_lock = threading.lock()

    def __init__(self, url):
        self.url = url
        self.camera = None
        self.connect()

    def connect(self):
        with StreamCamera._threading_lock:
            if self.camera is not None:
                try:
                    self.camera.release()

                except Exception as e:
                    print(f"카메라 해제 중 예외 발생: {e}")

            self.camera = cv2.VideoCapture(self.url)
            print("카메라가 연결되었습니다.")

    def is_opened(self):
        return self.camera is not None and self.camera.isOpened()

    def read_frame(self):
        if not self.is_opened():
            self.connect()
            return False, None

        with StreamCamera.lock:
            success, frame = self.camera.read()

        if not success:
            return False, None

        return True, frame


class FaceRecognizer:
    """InsightFace를 이용한 얼굴 DB 생성, JSON 저장/로드 및 유사도 비교 담당 클래스"""

    def __init__(self):
        self.face_app = FaceAnalysis(
            name="buffalo_l", providers=["CPUExecutionProvider"]
        )
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))

        # 런타임 매칭용 데이터 구조
        self.known_face_encodings = []
        self.known_face_names = []

    def load_or_build_db(self):
        """기존 JSON 파일이 있으면 로드하고, 없으면 신규 구축 후 JSON으로 저장"""
        if os.path.exists(FACES_ENCODINGS_FILE):
            self.load_from_json()
        else:
            self.build_and_save_json()

    def build_and_save_json(self):
        """폴더를 순회하며 특징점을 추출하고 JSON 형태로 저장"""
        json_data = {}
        target_counter = 1

        for massive_faces_dir in os.listdir(REG_DIR):
            face_dir = os.path.join(REG_DIR, massive_faces_dir)
            if not os.path.isdir(face_dir):
                continue

            print(f"[{massive_faces_dir}]의 사진들을 분석 중...")
            success_count = 0

            for filename in os.listdir(face_dir):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    path = os.path.join(face_dir, filename)
                    img = cv2.imread(path)

                    if img is None:
                        continue

                    faces = self.face_app.get(img)

                    if len(faces) > 0:
                        embedding_list = faces[0].normed_embedding.tolist()

                        # 유니크한 target_id 생성 (예: target_001)
                        target_id = f"target_{target_counter:03d}"

                        # 요청 양식에 맞춰 데이터 구조화: [ [이름], [특징점 벡터] ]
                        json_data[target_id] = [[massive_faces_dir], embedding_list]

                        target_counter += 1
                        success_count += 1

        with open(FACES_ENCODINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        # 메모리에 데이터 전개
        self._parse_json_to_memory(json_data)

    def load_from_json(self):
        """JSON 데이터베이스 파일 읽기"""
        with open(FACES_ENCODINGS_FILE, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        self._parse_json_to_memory(json_data)

    def _parse_json_to_memory(self, json_data):
        """JSON 구조를 연산을 위한 numpy 형태로 변환하여 메모리에 로드"""
        self.known_face_encodings = []
        self.known_face_names = []

        for target_id, data in json_data.items():
            name = data[0][0]
            embedding = np.array(data[1], dtype=np.float32)

            self.known_face_encodings.append(embedding)
            self.known_face_names.append(name)

        print(
            f">> 총 {len(set(self.known_face_names))}명, {len(self.known_face_names)}개의 유니크 Target DB 로드 완료.\n"
        )

    def identify_face(self, person_crop):
        """크롭된 영역에서 얼굴을 찾아 가장 매칭 점수가 높은 이름을 반환"""
        if len(self.known_face_encodings) == 0:
            return "Unknown"

        faces = self.face_app.get(person_crop)
        if len(faces) == 0:
            return "Unknown"

        current_embedding = faces[0].normed_embedding
        best_match = "Unknown"
        max_similarity = -1.0

        for known_embedding, name in zip(
            self.known_face_encodings, self.known_face_names
        ):
            similarity = np.dot(current_embedding, known_embedding)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = name

        # 임베딩 유사도 임계값 필터링
        if max_similarity > 0.42:
            return f"{best_match} ({max_similarity * 100:.0f}%)"

        return "Unknown"


class TrackingPipeline:
    """YOLO 추적 및 시각화 프로세스를 총괄하는 메인 파이프라인 클래스"""

    def __init__(self):
        self.camera = StreamCamera(ESP32_STREAM_URL)
        self.recognizer = FaceRecognizer()
        self.model = YOLO("yolov8n.pt")

        # 초기 디비 로드 또는 생성
        self.recognizer.load_or_build_db()

        # 트래킹 상태 기억
        self.tracked_identities = {}

    def process_frame(self):
        success, frame = self.camera.read_frame()
        if not success or frame is None:
            return None

        # YOLO + ByteTrack 사람(classes=[0]) 추적
        results = self.model.track(
            frame, persist=True, classes=[0], conf=0.5, verbose=False
        )
        result = results[0]

        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.int().cpu().tolist()
            track_ids = result.boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box

                # 경계값 처리
                y1, y2 = max(0, y1), min(frame.shape[0], y2)
                x1, x2 = max(0, x1), min(frame.shape[1], x2)

                # 처음 식별하는 Track ID인 경우에만 인물 감정 수행 (최적화)
                if track_id not in self.tracked_identities:
                    self.tracked_identities[track_id] = "Unknown"

                    person_crop = frame[y1:y2, x1:x2]
                    if person_crop.size > 0:
                        identity = self.recognizer.identify_face(person_crop)
                        self.tracked_identities[track_id] = identity

                # ----------------- 시각화 -----------------
                identity_label = self.tracked_identities.get(track_id, "Unknown")
                color = (0, 255, 0) if "Unknown" not in identity_label else (0, 0, 255)

                # 바운딩 박스 & 텍스트
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

                # 중심점
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.circle(frame, (center_x, center_y), 4, (255, 0, 0), -1)

        return frame


# 글로벌 호출용 인터페이스 규격 유지
pipeline = None


def get_frame():
    global pipeline
    if pipeline is None:
        pipeline = TrackingPipeline()
    return pipeline.process_frame()


def init_camera():
    global pipeline
    if pipeline is None:
        pipeline = TrackingPipeline()

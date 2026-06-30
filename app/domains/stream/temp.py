import json
import os
import threading
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from ultralytics import YOLO
from app.configs import REG_DIR

# 설정 및 상수
ESP32_STREAM_URL = "http://192.168.137.159:81/stream"
JSON_DB_PATH = os.path.join(REG_DIR, "face_database.json")


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

import cv2
from ultralytics import YOLO
from app.domains.stream import face_profiler

KEY_MATCH_RATIO = "FACE_MATCH_RATIO"
KEY_CROP = "PERSON_CROP"
KEY_BOX = "PERSON_BOX_IN_FRAME"

CONFIDENCE = 0.4
BOX_COLOR = (0, 0, 255)
THICKNESS = 5

_model = YOLO("yolov8n.pt")


# FIXME: thread_safe


def track_all(frames: list) -> list:
    """프레임 리스트를 받아 배치 처리하고 yolo모델로 분석시킨 프레임들을 반환"""
    frames_modified = [frame.copy() for frame in frames]
    results = find_people(frames_modified)

    for frame, result in zip(frames_modified, results):
        height, width, _ = frame.shape
        clamper = (0, 0, width, height)

        person_boxes = get_person_boxes(result)

        for box in person_boxes:
            clamped = clamp_box(box, clamper)
            draw_box_in_frame(frame, clamped)

    return frames_modified


def track_identify(frames: list) -> list:
    """프레임 리스트를 받아 배치 처리하고 DB에 등록된 사람만 바운딩 박스를 쳐서 반환"""
    frames_modified = [frame.copy() for frame in frames]
    results = find_people(frames_modified)

    for frame, result in zip(frames_modified, results):
        height, width, _ = frame.shape
        clamper = (0, 0, width, height)

        person_boxes = get_person_boxes(result)

        for box in person_boxes:
            clamped = clamp_box(box, clamper)
            crop = crop_frame(frame, clamped)

            user_id, match_ratio = face_profiler.identify(crop)

            if user_id == "":
                continue

            draw_box_in_frame(frame, clamped)

    return frames_modified


def get_person_boxes(result):
    if result.boxes is None and result.boxes.id is None:
        return []

    return result.boxes.xyxy.int().cpu().tolist()


def find_people(frames: list):
    results = _model.track(
        frames,
        persist=True,
        classes=[0],
        conf=CONFIDENCE,
        verbose=False,
        iou=0.5,
        tracker="botsort.yaml",
    )

    return results


def clamp_box(boundary_origin, clamper):
    x1, y1, x2, y2 = boundary_origin
    c_x1, c_y1, c_x2, c_y2 = clamper

    y1, y2 = max(c_y1, y1), min(c_y2, y2)
    x1, x2 = max(c_x1, x1), min(c_x2, x2)

    return (x1, y1, x2, y2)


def crop_frame(frame, boundary):
    if frame is None:
        return None

    x1, y1, x2, y2 = boundary
    return frame[y1:y2, x1:x2]


def draw_box_in_frame(frame, boundary):
    x1, y1, x2, y2 = boundary
    cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, THICKNESS)

    # center_x = (x1 + x2) // 2
    # center_y = (y1 + y2) // 2
    # cv2.circle(frame, (center_x, center_y), 4, (255, 0, 0), -1)

    return frame


if __name__ == "__main__":
    TEST_CASE = 1

    # from app.domains.stream.embedding_manager import build_and_save_face_embeddings
    # build_and_save_face_embeddings()
    from app.domains.stream import camera
    from app.domains.stream import face_profiler

    URL1 = "tests/newyork_street_01.mp4"
    URL2 = "tests/sibuya_street_01.mp4"

    if 1 == TEST_CASE:
        camera.add_camera(URL1, 0)
        camera.add_camera(URL2, 1)

        while True:
            ids = camera.get_all_camera_ids()
            frames = [camera.get_frame_by_id(id) for id in ids]
            frames = track_all(frames)

            for idx, frame in enumerate(frames):
                cv2.imshow(str(idx), frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    elif 2 == TEST_CASE:
        face_profiler.init_load_all_embeddings()
        camera.add_camera(0, 0)

        while True:
            frame = camera.get_frame_by_id(0)
            # cv2.imshow("show", frame)

            # frames = track_identify([frame])
            frames = track_all([frame])
            cv2.imshow("show", frames[0])

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from app.domains.stream import face_profiler

KEY_MATCH_RATIO = "FACE_MATCH_RATIO"
KEY_CROP = "PERSON_CROP"
KEY_BOX = "PERSON_BOX_IN_FRAME"

CONFIDENCE = 0.4
BOX_COLOR = (0, 0, 255)
THICKNESS = 5

_model = YOLO("yolov8n.pt")


def track_all(frames: list) -> list:
    """프레임을 리스트로 받아서 각 프레임들을 분석 후 발견한 사람 모두에게 주석을 달아서 반환"""
    frames_modified = [frame.copy() for frame in frames]
    results = find_people(frames_modified)

    return [r.plot() for r in results]


def track_identify(frames: list) -> list:
    """프레임을 리스트로 받아서 각 프레임들을 분석 후 db에 등록된 사람에게만 주석을 달아서 반환"""
    frames_modified = [frame.copy() for frame in frames]
    results = find_people(frames_modified)

    for frame, result in zip(frames_modified, results):
        if result.boxes is None or result.boxes.id is None:
            continue

        annotator = Annotator(frame, line_width=2)

        boxes = result.boxes.xyxy.int().cpu().tolist()
        track_ids = result.boxes.id.int().cpu().tolist()

        height, width, _ = frame.shape
        clamper = (0, 0, width, height)

        for box, track_id in zip(boxes, track_ids):
            clamped = clamp_box(box, clamper)
            crop = crop_frame(frame, clamped)

            user_id, match_ratio = face_profiler.identify(crop)

            if user_id == "":
                continue

            label = f"{user_id} ({match_ratio:.2f})"
            annotator.box_label(box, label, color=colors(track_id, True))

    return frames_modified


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


if __name__ == "__main__":
    TEST_CASE = 2

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
        camera.add_camera(0, 0, "stream")

        while True:
            frame = camera.get_frame_by_id(0)
            # cv2.imshow("show", frame)

            frames = track_identify([frame])
            # frames = track_all([frame])
            cv2.imshow("show", frames[0])

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

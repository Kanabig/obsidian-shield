import cv2
from ultralytics import YOLO


from app.domains.stream.identifier import identify_face
from app.configs import KEY_MATCH_RATIO, KEY_BOX, KEY_CROP

CONFIDENCE = 0.4
BOX_COLOR = (0, 0, 255)
THICKNESS = 5

model = YOLO("yolov8n.pt")

# TODO: 초기화 주기 정하기
already_tracked_ids = []

# FIXME: thread_safe


def track_all(FRAME_ORIGIN):
    frame_modified = FRAME_ORIGIN.copy()

    for box in generate_person_box(find_people(frame_modified)):
        height, width, _ = frame_modified.shape
        clamper = (0, 0, width, height)
        clamped_box = clamp_box(box, clamper)

        frame_modified = draw_box_in_frame(frame_modified, clamped_box)

    return frame_modified


def track(FRAME_ORIGIN):
    if FRAME_ORIGIN is None:
        return

    frame_modified = FRAME_ORIGIN.copy()
    person_datas = {}

    for box in generate_person_box(find_people(frame_modified)):
        height, width, _ = frame_modified.shape
        clamper = (0, 0, width, height)
        clamped = clamp_box(box, clamper)

        crop = crop_frame(frame_modified, clamped)
        person_id, match_ratio = identify_face(crop)

        if crop is None:
            continue

        if person_id == "":
            continue

        if person_id in person_datas:
            if person_datas[person_id][KEY_MATCH_RATIO] > match_ratio:
                continue

        person_datas[person_id] = {
            KEY_CROP: crop,
            KEY_MATCH_RATIO: match_ratio,
            KEY_BOX: clamped,
        }

    # 골라낸 사람 객체에 바운더리 그리기
    for data in person_datas.values():
        frame_modified = draw_box_in_frame(frame_modified, data[KEY_BOX])

    return frame_modified


def generate_person_box(result):
    if result.boxes is not None and result.boxes.id is not None:
        boxes = result.boxes.xyxy.int().cpu().tolist()
        track_ids = result.boxes.id.int().cpu().tolist()

        for box, track_id in zip(boxes, track_ids):
            # if track_id in already_tracked_ids:
            #     continue

            # already_tracked_ids.append(track_id)
            yield box


def find_people(frame):
    results = model.track(
        frame, persist=True, classes=[0], conf=CONFIDENCE, verbose=False
    )

    return results[0]


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
    TEST_CASE = 4

    # from app.domains.stream.embedding_manager import build_and_save_face_embeddings
    # build_and_save_face_embeddings()

    if 1 == TEST_CASE:
        frame_origin = cv2.imread("app/domains/stream/tests/people2.jpg")
        frame_modified = cv2.resize(
            frame_origin, dsize=(0, 0), fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA
        )
        result = find_people(frame_modified)
        person_box_gen = generate_person_box(result)

        for box in person_box_gen:
            height, width, _ = frame_modified.shape
            clamper = (0, 0, width, height)
            clamped_box = clamp_box(box, clamper)

            frame_modified = draw_box_in_frame(frame_modified, box)

        cv2.imshow("title", frame_modified)
        cv2.waitKey()

    elif 2 == TEST_CASE:
        frame_origin = cv2.imread("app/domains/stream/tests/people2.jpg")
        frame_modified = cv2.resize(
            frame_origin, dsize=(0, 0), fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA
        )
        result = find_people(frame_modified)
        person_box_gen = generate_person_box(result)
        person_crops = []

        for box in person_box_gen:
            height, width, _ = frame_modified.shape
            clamper = (0, 0, width, height)
            clamped_box = clamp_box(box, clamper)

            person_crops.append(crop_frame(frame_modified, clamped_box))

        for person_crop in person_crops:
            cv2.imshow("person", person_crop)
            cv2.waitKey()

    elif 3 == TEST_CASE:
        frame_origin = cv2.imread("app/domains/stream/tests/two.jpg")
        modified = frame_origin.copy()
        modified = track(modified)
        modified = cv2.resize(
            modified,
            dsize=(0, 0),
            fx=0.2,
            fy=0.2,
            interpolation=cv2.INTER_AREA,
        )
        cv2.imshow("title", modified)
        cv2.waitKey()

    elif 4 == TEST_CASE:
        from app.domains.stream.camera import StreamCamera

        path = "app/domains/stream/tests/newyork_street_01.mp4"

        cam = StreamCamera(path)

        while cam.is_opened():
            has_frame, frame = cam.read_frame()
            frame = track_all(frame)
            frame = cv2.resize(
                frame, dsize=(0, 0), fx=0.7, fy=0.7, interpolation=cv2.INTER_AREA
            )

            if not has_frame:
                continue

            cv2.imshow("Video", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

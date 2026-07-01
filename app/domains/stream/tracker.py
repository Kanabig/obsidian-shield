import cv2
from ultralytics import YOLO


from app.domains.stream import camera
from app.domains.stream.identifier import identify_face
from app.configs import ESP32_STREAM_URL

CONFIDENCE = 0.5
UNKNOWN = "UNKNOWN"

model = YOLO("yolov8n.pt")
# camera.add_camera(ESP32_STREAM_URL)
# camera.get_camera(ESP32_STREAM_URL).read_frame()

# TODO: 초기화 주기 정하기
tracked_identities = []


# FIXME: thread_safe
def make_tracked_frame(frame_origin):
    if frame_origin is None:
        return

    # 사람 찾기
    people_cropped = find_people_and_cropped(frame_origin)

    if people_cropped is None or len(people_cropped) == 0:
        return

    print("people count: ", len(people_cropped))

    # 등록된 사람 crop
    identified_people = {}
    matched_ratios = {}

    for person_cropped in people_cropped:
        person_img, _ = person_cropped
        person_id, match_ratio = identify_face(person_img)

        if person_id == "":
            continue

        print(person_id)

        # 이미 감지된 대상이면 신뢰도가 더 높은 대상만 crop
        if person_id in matched_ratios:
            if matched_ratios[person_id] >= match_ratio:
                continue

            identified_people[person_id] = person_cropped
            matched_ratios[person_id] = match_ratio

        identified_people[person_id] = person_cropped
        matched_ratios[person_id] = match_ratio

    print("identified people: ", len(identified_people))
    # 전체 프레임에서 crop된 사람 위치에 바운더리 그리기
    frame_modified = frame_origin

    for person in identified_people.values():
        _, boundary = person
        frame_modified = draw_boundary(frame_modified, boundary)

    return frame_modified


def find_people_and_cropped(frame):
    if frame is None:
        return None

    results = model.track(
        frame, persist=True, classes=[0], conf=CONFIDENCE, verbose=False
    )

    result = results[0]
    people_cropped = []

    if result.boxes is not None and result.boxes.id is not None:
        boxes = result.boxes.xyxy.int().cpu().tolist()
        track_ids = result.boxes.id.int().cpu().tolist()

        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = box

            # boundary 처리
            y1, y2 = max(0, y1), min(frame.shape[0], y2)
            x1, x2 = max(0, x1), min(frame.shape[1], x2)

            # 프레임에 처음 등장한 대상만 등록
            if track_id in tracked_identities:
                continue

            tracked_identities.append(track_id)
            person_crop = frame[y1:y2, x1:x2]

            if person_crop.size <= 0:
                continue

            people_cropped.append((person_crop, (x1, y1, x2, y2)))

    return people_cropped


def find_person_box_generator(result):
    already_tracked_ids = []

    if result.boxes is not None and result.boxes.id is not None:
        boxes = result.boxes.xyxy.int().cpu().tolist()
        track_ids = result.boxes.id.int().cpu().tolist()

        for box, track_id in zip(boxes, track_ids):
            if track_id in already_tracked_ids:
                continue

            already_tracked_ids.append(track_id)
            yield box


def find_people(frame):
    results = model.track(
        frame, persist=True, classes=[0], conf=CONFIDENCE, verbose=False
    )

    return results[0]


def clamp_boundary(boundary_origin, boundary_clamper):
    x1, y1, x2, y2 = boundary_origin
    c_x1, c_y1, c_x2, c_y2 = boundary_clamper

    y1, y2 = max(c_y1, y1), min(c_y2, y2)
    x1, x2 = max(c_x1, x1), min(c_x2, x2)
    # y1, y2 = max(0, y1), min(boundary_clamper.shape[0], y2)
    # x1, x2 = max(0, x1), min(boundary_clamper.shape[1], x2)

    return (x1, y1, x2, y2)


def crop_frame(frame, boundary):
    if frame is None:
        return None

    x1, y1, x2, y2 = boundary
    return frame[y1:y2, x1:x2]


def draw_boundary(frame, boundary):
    x1, y1, x2, y2 = boundary
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    cv2.circle(frame, (center_x, center_y), 4, (255, 0, 0), -1)

    return frame


if __name__ == "__main__":
    TEST_CASE = 2

    # from app.domains.stream.embedding_manager import build_and_save_face_embeddings
    # build_and_save_face_embeddings()

    if 1 == TEST_CASE:
        img = cv2.imread("app/domains/stream/tests/monster.png")
        people_cropped = find_people_and_cropped(img)

        for person_cropped in people_cropped:
            person_img, _ = person_cropped
            cv2.imshow("img", person_img)
            person_img = cv2.resize(
                person_img, dsize=(0, 0), fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA
            )
            cv2.waitKey()
            cv2.destroyAllWindows()

    elif 2 == TEST_CASE:
        img = cv2.imread("app/domains/stream/tests/two.jpg")
        img = make_tracked_frame(img)
        img = cv2.resize(
            img, dsize=(0, 0), fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA
        )
        cv2.imshow("img", img)
        cv2.waitKey()
        cv2.destroyAllWindows()

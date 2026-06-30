import numpy as np
from app.domains.stream.face_app_manager import face_app
from app.domains.stream.face_embedding_manager import load_face_embeddings

THREASHOLD = 0.42

# FIXME: Thread safe하게 변경


def identify_face(person_img_croped) -> str:
    """크롭된 영역에서 얼굴을 찾아 가장 매칭 점수가 높은 id 반환"""

    faces = face_app.get(person_img_croped)
    if len(faces) == 0:
        return ""

    recognized_embeddings = load_face_embeddings()
    current_embedding = faces[0].normed_embedding

    best_match = -1.0
    best_match_face_id = ""

    for face_id in recognized_embeddings:
        similarities = np.dot(recognized_embeddings[face_id], current_embedding)
        max_similarity = np.max(similarities)

        # 평균 유사도 판단
        # average_score = np.mean(similarities)

        if best_match < max_similarity:
            best_match = max_similarity
            best_match_face_id = face_id

    if best_match > THREASHOLD:
        return best_match_face_id

    return ""


if __name__ == "__main__":
    import cv2

    print("=====테스트 시작=====")
    img = cv2.imread("tests/face_sample/jungho2.jpg")
    print(f"best_match: {identify_face(img)}")
    print("=====테스트 종료=====")

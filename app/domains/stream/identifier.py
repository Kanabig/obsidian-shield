import numpy as np
from app.domains.stream.face_app_manager import face_app
from app.domains.stream.embedding_manager import load_face_embeddings
from app.configs import IDENTIFY_THREASHOLD


# FIXME: Thread safe하게 변경


def identify_face(person_img_croped) -> str:
    """
    입력받은 사람 이미지와 db에 등록된 검색 대상들과의 얼굴 특징점 비교
    유사도가 임계값 이상인 경우 반환: (target_id:str, match_ratio:float)
    유사도가 임계값 이하인 경우 반환: ("":str, -1.0:float)
    """

    NO_MATCH = ("", -1.0)

    faces = face_app.get(person_img_croped)
    if len(faces) == 0:
        return NO_MATCH

    recognized_embeddings = load_face_embeddings()
    current_embedding = faces[0].normed_embedding

    best_match_face_id, best_match_ratio = NO_MATCH

    for face_id in recognized_embeddings:
        similarities = np.dot(recognized_embeddings[face_id], current_embedding)
        max_similarity = np.max(similarities)

        # 평균 유사도 판단
        # average_score = np.mean(similarities)

        if best_match_ratio < max_similarity:
            best_match_ratio = max_similarity
            best_match_face_id = face_id

    if best_match_ratio > IDENTIFY_THREASHOLD:
        return (best_match_face_id, best_match_ratio)

    return NO_MATCH


if __name__ == "__main__":
    import cv2

    print("=====테스트 시작=====")
    img = cv2.imread("app/domains/stream/tests/face_01.jpg")
    print(f"best_match: {identify_face(img)}")
    print("=====테스트 종료=====")

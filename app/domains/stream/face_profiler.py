from insightface.app import FaceAnalysis
import threading
import numpy as np
from app.domains.stream.embedding_manager import load_face_embeddings
from app.utils.mute_print_and_warnings import mute_print_and_warnings

_instance = None
_lock = threading.Lock()


@mute_print_and_warnings
def _create_face_app():
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=0, det_size=FACE_DETECTION_SIZE)

    return app


def _get_face_app():
    global _instance

    # 병목 방지
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = _create_face_app()

    return _instance


FACE_DETECTION_SIZE = (640, 640)
IDENTIFY_THREASHOLD = 0.45
NO_MATCH = ("", -1.0)


def identify(person_img) -> tuple[str, float]:
    """
    입력받은 사람 이미지와 db에 등록된 검색 대상들과의 얼굴 특징점 비교
    유사도가 임계값 이상인 경우 반환: (target_id:str, match_ratio:float)
    유사도가 임계값 이하인 경우 반환: ("", -1.0)
    """
    app = _get_face_app()
    faces = app.get(person_img)

    if not faces:
        return NO_MATCH

    current_embedding = faces[0].normed_embedding
    # TODO: 캐싱
    recognized_embeddings = load_face_embeddings()

    if not recognized_embeddings:
        return NO_MATCH

    best_match_face_id, best_match_ratio = NO_MATCH

    for face_id in recognized_embeddings:
        similarities = np.dot(recognized_embeddings[face_id], current_embedding)
        max_similarity = np.max(similarities)

        # 평균 유사도 판단
        # average_score = np.mean(similarities)

        if max_similarity > best_match_ratio:
            best_match_ratio = max_similarity
            best_match_face_id = face_id

    if best_match_ratio < IDENTIFY_THREASHOLD:
        return NO_MATCH

    return (best_match_face_id, best_match_ratio)


if __name__ == "__main__":
    import cv2

    print("=====테스트 시작=====")
    img = cv2.imread("app/domains/stream/tests/face_01.jpg")
    print(f"best_match: {identify(img)}")
    print("=====테스트 종료=====")

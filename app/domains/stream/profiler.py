from insightface.app import FaceAnalysis
import os
from app.configs import FACES_DIR
from cv2 import imread
import numpy as np
from app.utils import log_deleter

EMBEDDINGS_FILE = "face_embeddings.npz"
THREASHOLD = 0.42
DETECTION_SIZE = (640, 640)


# FIXME: Thread safe하게 변경
class FaceProfiler:
    """InsightFace를 이용한 얼굴 DB 생성, JSON 저장/로드 및 유사도 비교 담당 클래스"""

    face_app = None

    def __init__(self):
        # FIXME: face_app은 프로그램 수명 전체에 걸쳐 하나만.
        if FaceProfiler.face_app is None:

            @log_deleter
            def initialize():
                FaceProfiler.face_app = FaceAnalysis(name="buffalo_l")
                self.face_app.prepare(ctx_id=0, det_size=DETECTION_SIZE)

            initialize()

    def build_embedding_from_face(self, person_img_croped):
        """사람의 사진으로부터 얼굴 특징점 추출"""
        if person_img_croped is None:
            return None

        faces = FaceProfiler.face_app.get(person_img_croped)
        return faces[0].normed_embedding if len(faces) > 0 else None

    def build_embedding_from_dir(self):
        """폴더를 순회하며 특징점을 추출하고 ndarray로 저장"""
        print("임베딩 추출 시작")
        if not os.path.exists(FACES_DIR):
            raise Exception(f"{FACES_DIR}폴더가 없습니다.")

        face_embeddings = {}

        # TODO: 깊이 기반 탐색으로 변경
        for face_id in os.listdir(FACES_DIR):
            face_dir = os.path.join(FACES_DIR, face_id)
            face_embeddings[face_id] = []

            if not os.path.isdir(face_dir):
                continue

            for filename in os.listdir(face_dir):
                if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    print(f"{filename}은 이미지 파일이 아닙니다.")
                    continue

                path = os.path.join(face_dir, filename)
                img = imread(path)
                embedding = self.build_embedding_from_face(img)

                if embedding is None:
                    print(f"실패 (얼굴 인식 불가): {filename}")
                    continue

                face_embeddings[face_id].append(embedding)

        np.savez_compressed(EMBEDDINGS_FILE, **face_embeddings)
        print("임베딩 추출 종료")

    def load_face_embeddings(self):
        return np.load(EMBEDDINGS_FILE, allow_pickle=True)

    def identify_face(self, person_img_croped) -> str:
        """크롭된 영역에서 얼굴을 찾아 가장 매칭 점수가 높은 id 반환"""

        faces = FaceProfiler.face_app.get(person_img_croped)
        if len(faces) == 0:
            return ""

        recognized_embeddings = self.load_face_embeddings()
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
    face_recog = FaceProfiler()

    face_recog.build_embedding_from_dir()
    # loads = face_recog.load_face_embeddings()
    # print(loads["jungho001"])

    img = cv2.imread("tests/face_sample/jungho2.jpg")
    print(f"best_match: {face_recog.identify_face(img)}")
    print("=====테스트 종료=====")

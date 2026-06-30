from insightface.app import FaceAnalysis
import os
from app.configs import FACES_DIR
from cv2 import imread
import numpy as np

EMBEDDINGS_FILE = "face_embeddings.npz"
THREASHOLD = 0.42
DETECTION_SIZE = (640, 640)


# FIXME: Thread safe하게 변경
class FaceProfiler:
    """InsightFace를 이용한 얼굴 DB 생성, JSON 저장/로드 및 유사도 비교 담당 클래스"""

    def __init__(self):
        self.face_app = FaceAnalysis(
            name="buffalo_l", providers=["CPUExecutionProvider"]
        )
        self.face_app.prepare(ctx_id=0, det_size=DETECTION_SIZE)

    def build_embedding_from_faces(self):
        """폴더를 순회하며 특징점을 추출하고 ndarray로 저장"""
        if not os.path.exists(FACES_DIR):
            raise Exception(f"{FACES_DIR}폴더가 없습니다.")

        face_embeddings = {}

        for face_id in os.listdir(FACES_DIR):
            face_dir = os.path.join(FACES_DIR, face_id)
            face_embeddings[face_id] = []

            if not os.path.isdir(face_dir):
                continue

            for filename in os.listdir(face_dir):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    path = os.path.join(face_dir, filename)
                    img = imread(path)

                    if img is None:
                        continue

                    faces = self.face_app.get(img)

                    if len(faces) > 0:
                        # 특징점 벡터 <class 'numpy.ndarray'>.tolist()
                        # FIXME: 여기서 tolist()를 하지 않고 저장
                        embedding_list = faces[0].normed_embedding.tolist()
                        face_embeddings[face_id].append(embedding_list)

                    else:
                        print(f"실패 (얼굴 인식 불가): {filename}")

        np.savez_compressed(EMBEDDINGS_FILE, **face_embeddings)

    def load_face_embeddings(self):
        return np.load(EMBEDDINGS_FILE, allow_pickle=True)

    def identify_face(self, person_img_croped) -> str:
        """크롭된 영역에서 얼굴을 찾아 가장 매칭 점수가 높은 id 반환"""

        print("in scope")
        faces = self.face_app.get(person_img_croped)
        if len(faces) == 0:
            return ""

        print("get embeddings")
        current_embedding = faces[0].normed_embedding
        recognized_embeddings = self.load_face_embeddings()

        best_match = -1.0

        for face_id in recognized_embeddings:
            print("np.dot empeddings")
            similarities = np.dot(recognized_embeddings[face_id], current_embedding)
            max_similarity = np.max(similarities)
            # average_score = np.mean(similarities) 유사도 판단

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
    img = cv2.imread(f"{FACES_DIR}/face_sample/jungho2.jpg")
    print(f"best_match: {face_recog.identify_face(img)}")
    print("=====테스트 종료=====")

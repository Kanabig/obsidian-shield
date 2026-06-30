from insightface.app import FaceAnalysis
import os
from app.configs import FACES_DIR
from app.utils.json_manager import save_json, load_json, FACES_ENCODINGS_FILE
from cv2 import imread
import numpy as np


class FaceRecognizer:
    """InsightFace를 이용한 얼굴 DB 생성, JSON 저장/로드 및 유사도 비교 담당 클래스"""

    def __init__(self):
        self.face_app = FaceAnalysis(
            name="buffalo_l", providers=["CPUExecutionProvider"]
        )
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))

        # 런타임 매칭용 데이터 구조

    def make_face_encodings(self):
        """폴더를 순회하며 특징점을 추출하고 요청된 JSON 형태로 저장"""
        if not os.path.exists(FACES_DIR):
            raise Exception(f"{FACES_DIR}폴더가 없습니다.")

        # face_encodings = self.load_face_encodings()
        face_encodings = {}

        for face_id in os.listdir(FACES_DIR):
            face_dir = os.path.join(FACES_DIR, face_id)
            face_encodings[face_id] = []

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
                        embedding_list = faces[0].normed_embedding.tolist()
                        face_encodings[face_id].append(embedding_list)

                    else:
                        print(f"  └ 실패 (얼굴 인식 불가): {filename}")

        save_json(FACES_ENCODINGS_FILE, face_encodings)

    def load_face_encodings(self):
        return self._parse_json_to_ndarray(load_json(FACES_ENCODINGS_FILE))

    def _parse_json_to_ndarray(self, json_data):
        """불러온 json데이터를 numpy 형태로 변환"""
        ndarray_embeddings = {}

        for face_id, embeddings_list in json_data.items():
            # 리스트 내부의 각 임베딩 리스트를 넘파이 배열로 변환
            ndarray_embeddings[face_id] = [
                np.array(emb, dtype=np.float32) for emb in embeddings_list
            ]

        return ndarray_embeddings

    def identify_face(self, person_crop):
        """크롭된 영역에서 얼굴을 찾아 가장 매칭 점수가 높은 이름을 반환"""
        if len(self.face_encodings_in_memory) == 0:
            return "Unknown"

        faces = self.face_app.get(person_crop)
        if len(faces) == 0:
            return "Unknown"

        current_embedding = faces[0].normed_embedding
        best_match = "Unknown"
        max_similarity = -1.0

        for known_embedding, name in zip(
            self.face_encodings_in_memory, self.known_face_names
        ):
            similarity = np.dot(current_embedding, known_embedding)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = name

        # 임베딩 유사도 임계값 필터링
        if max_similarity > 0.42:
            return f"{best_match} ({max_similarity * 100:.0f}%)"

        return "Unknown"


if __name__ == "__main__":
    # print(os.path.exists(FACES_DIR))
    # print(FACES_DIR)
    print("=====테스트 시작=====")
    faceRecog = FaceRecognizer()
    print("face recog initialize")
    faceRecog.make_face_encodings()
    print(faceRecog.load_face_encodings())
    print("=====테스트 종료=====")

    # np.savez_compressed('face_encodings.npz', **face_encodings)

    # # 불러올 때
    # loaded = np.load('face_encodings.npz', allow_pickle=True)
    # # 원래 구조 그대로 float32 배열로 즉시 복원됨
    # face_1_embeddings = loaded['face_1']

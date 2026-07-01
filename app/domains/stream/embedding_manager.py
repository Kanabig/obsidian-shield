import os
from cv2 import imread
import numpy as np
from app.utils.json_manager import BASE_DIR

from app.domains.stream.face_app_manager import face_app

FACE_EMBEDDINGS_FILE = os.path.join(BASE_DIR, "jsons", "face_embeddings.npz")
REGISTERED_FACES_DIR = os.path.join(
    BASE_DIR, "domains", "stream", "static", "registered_faces"
)


def build_embedding_from_face(person_img_croped):
    """사람의 사진으로부터 얼굴 특징점 추출"""
    if person_img_croped is None:
        return None

    faces = face_app.get(person_img_croped)
    return faces[0].normed_embedding if len(faces) > 0 else None


def build_and_save_face_embeddings():
    """폴더를 순회하며 특징점을 추출하고 ndarray로 저장"""
    print("임베딩 추출 시작")
    if not os.path.exists(REGISTERED_FACES_DIR):
        raise Exception(f"{REGISTERED_FACES_DIR}폴더가 없습니다.")

    face_embeddings = {}

    # TODO: 깊이 기반 탐색으로 변경
    for face_id in os.listdir(REGISTERED_FACES_DIR):
        face_dir = os.path.join(REGISTERED_FACES_DIR, face_id)
        face_embeddings[face_id] = []

        if not os.path.isdir(face_dir):
            continue

        for filename in os.listdir(face_dir):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                print(f"{filename}은 이미지 파일이 아닙니다.")
                continue

            path = os.path.join(face_dir, filename)
            img = imread(path)
            embedding = build_embedding_from_face(img)

            if embedding is None:
                print(f"실패 (얼굴 인식 불가): {filename}")
                continue

            face_embeddings[face_id].append(embedding)

    np.savez_compressed(FACE_EMBEDDINGS_FILE, **face_embeddings)
    print("임베딩 추출 종료")


def load_face_embeddings():
    return np.load(FACE_EMBEDDINGS_FILE, allow_pickle=True)


# if __name__ == "__main__":
# build_and_save_embedding()
# embeddings = load_face_embeddings()
# print(embeddings["jungho001"])

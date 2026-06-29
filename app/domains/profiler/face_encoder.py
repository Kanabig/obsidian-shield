from app.configs import REG_DIR
from insightface.app import FaceAnalysis
import os
import cv2
from app.utils import json_manager

# 저사양 환경을 고려(320x320)
FACE_DET_SIZE = (320, 320)

face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0, det_size=FACE_DET_SIZE)

# 3) 신원 데이터베이스 및 트래킹 변수
target_face_encodings = []
known_face_names = []


def build_face_db():
    global target_face_encodings, known_face_names

    if not os.path.exists(REG_DIR):
        os.makedirs(REG_DIR)
        print(f"'{REG_DIR}'폴더가 존재하지 않아 새로 생성되었습니다.")
        return

    for dir_name in os.listdir(REG_DIR):
        face_dir = os.path.join(REG_DIR, dir_name)

        if not os.path.isdir(face_dir):
            continue

        success_count = 0

        # 2단계: 각 사람 폴더 안의 이미지 파일 루프
        for filename in os.listdir(face_dir):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(face_dir, filename)
                img = cv2.imread(path)

                if img is None:
                    continue

                # InsightFace로 얼굴 분석
                faces = face_app.get(img)

                if len(faces) > 0:
                    # 얼굴 임베딩 데이터와 매칭될 '폴더명(이름)'을 저장
                    target_face_encodings.append(faces[0].normed_embedding)
                    known_face_names.append(
                        dir_name
                    )  # 파일명이 아니라 폴더명을 이름으로 사용!
                    success_count += 1
                else:
                    print(f"  └ 실패 (얼굴 인식 불가): {filename}")

        if success_count > 0:
            print(f"  └ {dir_name} 등록 완료 ({success_count}장의 사진)")

    print(
        f">> 총 {len(set(known_face_names))}명, {len(known_face_names)}개의 얼굴 DB 구축 완료.\n"
    )

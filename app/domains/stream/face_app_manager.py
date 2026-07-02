from insightface.app import FaceAnalysis
from contextlib import redirect_stderr, redirect_stdout
import os
import warnings
from app.configs import FACE_DETECTION_SIZE

warnings.filterwarnings("ignore", category=FutureWarning)


face_app = None


def initialize():
    global face_app

    if face_app is not None:
        return

    with open(os.devnull, "w") as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            # providers=["CPUExecutionProvider"]
            face_app = FaceAnalysis(name="buffalo_l")
            face_app.prepare(ctx_id=0, det_size=FACE_DETECTION_SIZE)


initialize()

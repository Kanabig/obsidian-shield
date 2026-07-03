import threading
import time
import numpy as np
from cv2 import VideoCapture


class StreamCamera:
    """백그라운드(thread)에서 카메라의 프레임을 확보 및 제공하는 클래스"""

    def __init__(self, source):
        self.source = source
        self.camera = None

        self.lock = threading.Lock()
        self.on_running = False
        self.thread = None

        # 최초에 아무런 프레임도 습득하지 못했을 때 검은 화면 송출
        self.latest_frame = np.zeros((1080, 1920, 3), np.uint8)

        self.connect()
        self.start()

    def connect(self):
        if self.camera is not None:
            try:
                self.camera.release()

            except Exception as e:
                print(f"카메라 해제 중 예외 발생: {e}")

        self.camera = VideoCapture(self.source)

    def start(self):
        if not self.on_running:
            self.on_running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()

    def _capture_loop(self):
        while self.on_running:
            if self.camera is None or not self.camera.isOpened():
                self.connect()
                continue

            success, frame = self.camera.read()

            if success:
                with self.lock:
                    self.latest_frame = frame

            # CPU 과점유 방지(framerate 설정)
            time.sleep(0.0416)

    def read_frame(self):
        with self.lock():
            return self.latest_frame

    def release(self):
        self.on_running = False

        if self.thread is not None:
            self.thread.join()

        if self.camera.isOpened():
            self.camera.release()


# ================
# 카메라 관리 함수들
# ================
cameras = {}


def add_camera(source, id):
    if id in cameras:
        print("이미 등록된 카메라입니다.")
        return

    cameras[id] = StreamCamera(source)


def delete_camera(id):
    if id not in cameras:
        return

    cam = cameras[id]
    del cameras[id]

    # 안전 release
    threading.Thread(target=cam.release, daemon=True).start()


def get_frame_by_id(id):
    if id not in cameras:
        return None

    frame = cameras[id].read_frame()

    return frame


def get_all_camera_ids():
    return cameras.keys()


if __name__ == "__main__":
    import cv2

    TEST_CASE = 1

    URL1 = "app/domains/stream/tests/newyork_street_01.mp4"
    URL2 = "app/domains/stream/tests/sibuya_street_01.mp4"

    add_camera(URL1, 0)
    add_camera(URL2, 1)

    if TEST_CASE == 1:
        while True:
            ids = get_all_camera_ids()

            for id in ids:
                frame = get_frame_by_id(id)

                if frame is None:
                    continue

                cv2.imshow(str(id), frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    elif TEST_CASE == 2:
        step = 0

        while True:
            frame01 = get_frame_by_id(0)
            frame02 = get_frame_by_id(1)

            if frame01 is not None:
                cv2.imshow("Video01", frame01)

            if frame02 is not None:
                cv2.imshow("Video02", frame02)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                if step == 0:
                    delete_camera(0)
                    step += 1
                    continue

                break

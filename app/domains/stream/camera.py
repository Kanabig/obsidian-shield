import threading
import time
import numpy as np
from cv2 import VideoCapture
from cv2 import CAP_PROP_FPS

VIDEO = "video"
BLACK_SCREEN = np.zeros((1080, 1920, 3), np.uint8)

FRAME_DEFAULT = 60
CONNECT_DELAY = 0.5
UNSTABLE_STREAMING_DELAY = 0.1
CPU_USAGE_DELAY = 0.001

_instances = {}


class Camera:
    """
    백그라운드(thread)에서 카메라의 최신 프레임을 확보 및 제공하는 클래스.
    최초 생성시 아무런 프레임도 확보하지 못하면 검은 화면 반환
    """

    def __init__(self, src_path, src_type=VIDEO):
        self.src_path = src_path
        self.src_type = src_type
        self.camera = None

        self.on_running = False
        self.thread = None
        self.lock = threading.Lock()

        self.latest_frame = BLACK_SCREEN.copy()

        self.connect()
        self.start()

    def connect(self):
        if self.camera is not None:
            self.camera.release()

        self.camera = VideoCapture(self.src_path)

    def start(self):
        if not self.on_running:
            self.on_running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()

    def _capture_loop(self):

        is_video = self.src_type == VIDEO

        fps = self.camera.get(CAP_PROP_FPS) if is_video else FRAME_DEFAULT
        fps = fps if fps != 0 else FRAME_DEFAULT

        # framerate or cpu 과점유 딜레이
        frame_delay = 1.0 / fps if is_video else CPU_USAGE_DELAY

        while self.on_running:
            if self.camera is None or not self.camera.isOpened():
                self.connect()
                # 무한 재연결 시도 예방 딜레이
                time.sleep(CONNECT_DELAY)
                continue

            success, frame = self.camera.read()

            if success:
                with self.lock:
                    self.latest_frame = frame

                time.sleep(frame_delay)

            else:
                if is_video:
                    # 동영상 시작 지점으로 되감기
                    self.camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    # 스트리밍 불안정시 프레임 확보용 딜레이
                    time.sleep(UNSTABLE_STREAMING_DELAY)

    def read_frame(self):
        with self.lock:
            return self.latest_frame.copy()

    def release(self):
        self.on_running = False

        if self.thread is not None:
            self.thread.join()

        if self.camera.isOpened():
            self.camera.release()


# ================
# 카메라 관리 함수들
# ================


def add_camera(source, id):
    if id in _instances:
        print("이미 등록된 카메라입니다.")
        return

    _instances[id] = Camera(source)


def delete_camera(id):
    if id not in _instances:
        return

    cam = _instances[id]
    del _instances[id]

    # 안전 release
    threading.Thread(target=cam.release, daemon=True).start()


def clear():
    for camera in _instances():
        delete_camera(id)


def get_frame_by_id(id):
    if id not in _instances:
        return BLACK_SCREEN.copy()

    return _instances[id].read_frame()


def get_all_camera_ids():
    return tuple(_instances.keys())


if __name__ == "__main__":
    import cv2

    TEST_CASE = 1

    URL1 = "tests/newyork_street_01.mp4"
    URL2 = "tests/sibuya_street_01.mp4"

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

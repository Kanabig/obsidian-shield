import threading
import time
from cv2 import VideoCapture


class StreamCamera:
    """백그라운드(thread)에서 카메라의 프레임을 확보 및 제공하는 클래스"""

    def __init__(self, url):
        self.url = url
        self.camera = None

        self.lock = threading.Lock()
        self.running = False
        self.thread = None

        self.latest_frame = None
        self.has_frame = False

        self.connect()
        self.start()

    def connect(self):
        if self.camera is not None:
            try:
                self.camera.release()

            except Exception as e:
                print(f"카메라 해제 중 예외 발생: {e}")

        self.camera = VideoCapture(self.url)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()

    def _capture_loop(self):
        while self.running:
            if self.camera is None or not self.camera.isOpened():
                self.connect()
                continue

            success, frame = self.camera.read()

            if success:
                with self.lock:
                    self.latest_frame = frame
                    self.has_frame = True

            else:
                with self.lock:
                    self.has_frame = False

                self.connect()

            # CPU 과점유 방지(framerate 설정)
            time.sleep(0.0416)

    def read_frame(self):
        return self.has_frame, self.latest_frame

    def release(self):
        self.running = False

        if self.thread is not None:
            self.thread.join(1)

        if self.camera.isOpened():
            self.camera.release()


# ================
# 카메라 관리 함수들
# ================
cameras = {}
cameras_id = {}
index = 0


def add_camera(url):
    global index

    if url in cameras:
        print("이미 등록된 카메라입니다.")
        return

    cameras[url] = StreamCamera(url)
    cameras_id[index] = url

    index += 1


def delete_camera(url):
    if url not in cameras:
        return

    cam = cameras[url]
    del cameras[url]

    # 안전 release
    threading.Thread(target=cam.release, daemon=True).start()


def get_frame_by_url(url):
    if url not in cameras:
        return None

    has_frame, frame = cameras[url].read_frame()

    if not has_frame:
        return None

    return frame


def get_frame_by_id(id):
    if id not in cameras_id:
        return None

    return get_frame_by_url(cameras_id[id])


if __name__ == "__main__":
    import cv2

    URL1 = "app/domains/stream/tests/newyork_street_01.mp4"
    URL2 = "app/domains/stream/tests/sibuya_street_01.mp4"

    add_camera(URL1)
    add_camera(URL2)

    while True:
        frame01 = get_frame_by_id(0)
        frame02 = get_frame_by_id(1)

        if frame01 is not None:
            cv2.imshow("Video01", frame01)

        if frame02 is not None:
            cv2.imshow("Video02", frame02)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

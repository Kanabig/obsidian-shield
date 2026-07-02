import threading
from cv2 import VideoCapture


class StreamCamera:
    """스트림 카메라 연결, 프레임 수급"""

    _threading_lock = threading.Lock()

    def __init__(self, url):
        self.url = url
        self.camera = None
        self.connect()

    def connect(self):
        with StreamCamera._threading_lock:
            if self.camera is not None:
                try:
                    self.camera.release()

                except Exception as e:
                    print(f"카메라 해제 중 예외 발생: {e}")

            self.camera = VideoCapture(self.url)
            print("카메라가 연결되었습니다.")

    def is_opened(self):
        return self.camera is not None and self.camera.isOpened()

    def read_frame(self):
        if not self.is_opened():
            self.connect()
            return False, None

        with StreamCamera._threading_lock:
            success, frame = self.camera.read()

        if not success:
            return False, None

        return True, frame


cameras = {}


def add_camera(url):
    if url in cameras:
        print("이미 등록된 카메라입니다.")
        return

    cameras[url] = StreamCamera(url)


def get_frame(url):
    has_frame, frame = cameras[url].read_frame()

    if not has_frame:
        return None

    return frame


def get_frames(*urls):
    frames = {}

    for url in urls:
        frames[url] = get_frame(url)

    return frames


if __name__ == "__main__":
    import cv2

    URL1 = "app/domains/stream/tests/dessert.mp4"
    URL2 = "app/domains/stream/tests/grassland.mp4"

    add_camera(URL1)
    add_camera(URL2)

    frames = get_frames(URL1, URL2)

    if len(frames) != 0:
        for frame in frames.values():
            if frame is None:
                continue

            cv2.imshow("frame", frame)
            cv2.waitKey(0)

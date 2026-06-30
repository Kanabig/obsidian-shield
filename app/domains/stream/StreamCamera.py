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


if __name__ == "__main__":
    import cv2

    cam = StreamCamera("test.mp4")
    success, frame = cam.read_frame()
    cv2.imshow("frame", frame)
    cv2.waitKey(0)

from app.domains.stream import camera
from app.domains.stream import tracker
import threading


class FrameAnalyzer:
    def __init__(self):
        self.thread = None
        self.lock = threading.Lock()
        self.on_running = False

        self.latest_frames = {}
        self.start()

    def start(self):
        if not self.on_running:
            self.on_running = True
            self.thread = threading.Thread(target=self._analyze_loop, daemon=True)
            self.thread.start()

    def _analyze_loop(self):
        while self.on_running:
            camera_ids = camera.get_all_camera_ids()
            camera_frames = {}

            for id in camera_ids:
                camera_frames[id] = camera.get_frame_by_id(id)

            tracker.track_all()

    def stop(self):
        self.on_running = False

        if self.thread is not None:
            self.thread.join()


frame_analyzer = FrameAnalyzer()


def get_latest_frames():
    return frame_analyzer.latest_frames


if __name__ == "__main__":
    import cv2

    URL1 = "app/domains/stream/tests/newyork_street_01.mp4"
    URL2 = "app/domains/stream/tests/sibuya_street_01.mp4"

    camera.add_camera(URL1, 0)
    camera.add_camera(URL2, 1)

    while True:
        frames = get_latest_frames()

        if frames is None or len(frames) == 0:
            continue

        for id in frames:
            if frames[id] is None:
                continue

            cv2.imshow("id", frames[id])

import time

from flask import Blueprint, Response, render_template, request
from cv2 import imencode

from app.domains.stream import analysis_pipeline
# from app.domains.stream import face_profiler
# from app.domains.stream import camera

stream_bp = Blueprint(
    "stream",
    __name__,
    url_prefix="/stream",
    template_folder="templates",
    static_folder="static",
    static_url_path="/stream/static",
)

# app.py로 옮겨야 하는 코드
# face_profiler.init_load_all_embeddings()
# camera.add_camera("tests/sibuya_street_01.mp4", 0)


@stream_bp.route("/")
def stream():
    return render_template("stream_main.html")


@stream_bp.route("/video_feed/")
def video_feed():

    cam_id = request.args.get("cam_id", "0", type=int)

    return Response(
        generate_frames(cam_id),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def generate_frames(cam_id):
    while True:
        frames = analysis_pipeline.get_latest_frames()
        frame = frames[cam_id]

        if frame is None:
            time.sleep(0.1)
            continue

        ret, buffer = imencode(".jpg", frame)

        if not ret:
            time.sleep(0.1)
            continue

        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        time.sleep(0.01)

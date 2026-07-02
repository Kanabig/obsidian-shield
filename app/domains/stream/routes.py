from flask import Blueprint, Response, render_template, request
from app.domains.stream import camera
from app.domains.stream import tracker
import time
import cv2

stream_bp = Blueprint(
    "stream", __name__, url_prefix="/stream", template_folder="templates"
)


@stream_bp.route("/")
def stream():
    return render_template("index.html")


@stream_bp.route("/video_feed/")
def video_feed():

    cam_id = request.args.get("cam_id", "0", type=int)

    return Response(
        generate_frames(cam_id),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def generate_frames(cam_id):
    while True:
        frame = camera.get_frame_by_id(cam_id)

        if frame is None:
            continue

        tracked_frame = tracker.track_all(frame)

        if tracked_frame is None:
            time.sleep(0.1)
            continue

        ret, buffer = cv2.imencode(".jpg", tracked_frame)

        if not ret:
            time.sleep(0.1)
            continue

        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        time.sleep(0.03)

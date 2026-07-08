import time
import os

from flask import Blueprint, Response, render_template, request, redirect, url_for
from cv2 import imdecode, imencode, IMREAD_COLOR
from numpy import frombuffer, uint8
from werkzeug.utils import secure_filename

from app.domains.stream import analysis_pipeline
from app.domains.stream import camera as camera_manager
from app.domains.stream.face_profiler import add_or_update_face

from app.utils.pagination import paginate
from app.utils.json_manager import load_json, save_json, TARGETS_PROFILES_FILE
from app.utils.time_stamper import get_current_time_stamp_formated

from app.utils.member_filter import filter_keyword
from app.utils.member_sort import sort_accounts

stream_bp = Blueprint(
    "stream",
    __name__,
    url_prefix="/stream",
    template_folder="templates",
    static_folder="static",
    static_url_path="/stream/static",
)


@stream_bp.route("/monitoring")
def monitoring():
    camera_ids = camera_manager.get_all_camera_ids()
    return render_template("stream_main.html", camera_ids=camera_ids)


@stream_bp.route("/camera/", methods=["GET", "POST"])
def camera():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            cam_id = request.form.get("cam_id")
            src_path = request.form.get("src_path")
            src_type = request.form.get("src_type", "video")  # 기본값은 video

            if cam_id and src_path:
                camera_manager.add_camera(
                    src_path=src_path, id=cam_id, src_type=src_type
                )

        elif action == "delete":
            cam_id = request.form.get("cam_id")
            if cam_id:
                camera_manager.delete_camera(cam_id)

        return redirect(url_for("stream.camera"))

    active_cameras = []
    for cid in camera_manager.get_all_camera_ids():
        cam_obj = camera_manager.get_camera_by_id(cid)
        if cam_obj:
            active_cameras.append(
                {"id": cid, "src_path": cam_obj.src_path, "is_video": cam_obj.is_video}
            )

    return render_template("camera_main.html", cameras=active_cameras)


@stream_bp.route("/profile/", methods=["GET", "POST"])
def profile():
    # 프로필 CRUD 및 안면 인식 처리
    if request.method == "POST":
        profiles = load_json(TARGETS_PROFILES_FILE)
        action = request.form.get("action")

        # [기존] 등록 기능
        if action == "add":
            id = request.form.get("id")
            name = request.form.get("name")
            age = request.form.get("age")
            desc_short = request.form.get("description_short")
            desc_long = request.form.get("description_long")

            file = request.files.get("profile_img")
            upload_path = os.path.join(stream_bp.static_folder, "uploaded_profiles")
            os.makedirs(upload_path, exist_ok=True)
            file_name = secure_filename(f"{id}_{file.filename}")
            file.save(os.path.join(upload_path, file_name))

            time_formatted = get_current_time_stamp_formated()
            profiles[id] = {
                "ID": id,
                "NAME": name,
                "AGE": age,
                "SHORT_DESCRIPTION": desc_short,
                "DESCRIPTION": desc_long,
                "IMAGE": file_name,
                "REG_DATE": time_formatted,
                "MOD_DATE": time_formatted,
            }

        elif action == "update":
            id = request.form.get("id")
            if id in profiles:
                profiles[id]["NAME"] = request.form.get("name")
                profiles[id]["AGE"] = request.form.get("age")
                profiles[id]["SHORT_DESCRIPTION"] = request.form.get(
                    "description_short"
                )
                profiles[id]["DESCRIPTION"] = request.form.get("description_long")
                profiles[id]["MOD_DATE"] = get_current_time_stamp_formated()

                file = request.files.get("profile_img")
                upload_path = os.path.join(stream_bp.static_folder, "uploaded_profiles")
                os.makedirs(upload_path, exist_ok=True)
                file_name = secure_filename(f"{id}_{file.filename}")
                profiles[id]["IMAGE"] = file_name
                file.save(os.path.join(upload_path, file_name))

        elif action == "face_encode":
            id = request.form.get("id")
            face_file = request.files.get("face_img")
            if face_file and face_file.filename != "":
                file_bytes = face_file.read()
                img = imdecode(frombuffer(file_bytes, dtype=uint8), IMREAD_COLOR)
                add_or_update_face(id, img)

        elif action == "delete":
            id = request.form.get("id")
            if id in profiles:
                del profiles[id]

        save_json(TARGETS_PROFILES_FILE, profiles)
        return redirect(url_for("stream.profile"))

    # GET: 검색, 정렬, 페이지네이션
    profiles_list = list(load_json(TARGETS_PROFILES_FILE).values())
    kwd = request.args.get("search_keyword")
    tag = request.args.get("search_tag")
    profiles_list = filter_keyword(profiles_list, kwd, tag)

    order = request.args.get("sort_order")
    profiles_list = sort_accounts(profiles_list, order)

    per_page = int(request.args.get("per_page", 10))
    page = int(request.args.get("page", 1))
    profiles_paginated, total_pages = paginate(profiles_list, page, per_page)

    return render_template(
        "profile_main.html",
        profiles=profiles_paginated,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@stream_bp.route("/video_feed/")
def video_feed():

    cam_id = request.args.get("cam_id", "0")

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

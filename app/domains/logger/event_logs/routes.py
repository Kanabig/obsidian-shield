from flask import Blueprint, render_template, request
from app.domains.logger.event_logs.event_logs import (
    get_event_list,add_event,format_events,
    checked_event_logs)
from app.domains.logger.logger_utils.log_utils import (
    create_excel_file, download_excel_file)
from app.utils.pagination import paginate


event_log_bp = Blueprint(
    "event_log",
    __name__,
    url_prefix="/event_log",
    template_folder="../templates",
    static_folder="../static"
)

@event_log_bp.route("/event_log_list")
def event_list():

    events = get_event_list()

    per_page = request.args.get("per_page", default=10, type=int)
    page = request.args.get("page", default=1, type=int)

    events, total_pages = paginate(
        events, 
        page, 
        per_page)

    return render_template(
        "event_log_list.html", 
        events = events,
        per_page = per_page,
        page = page,
        total_pages = total_pages)
    

@event_log_bp.route("/export_event_data")
def export_event_data():

    events = get_event_list()

    cleaned_events = format_events(events)

    output = create_excel_file(
        cleaned_events, 
        sheet_name="Event_Logs")

    return download_excel_file(
        output, 
        "event_logs.xlsx")


@event_log_bp.route("/add_event", methods=["POST"])
def add_event_log():

    data = request.get_json()

    if not data:
        return {
            "result": "fail", 
            "message": "Invalid JSON data"
        }, 400
     
    add_event(data)

    return {"result": "success"}, 201


@event_log_bp.route("/checked_event_log", methods=["POST"])
def checked_event():

    data = request.get_json()

    checked_event_logs(
        data["ids"],
        data["viewer_id"]
    )

    return {"result": "success"}

from flask import Blueprint, render_template
from app.domains.logger.user_logs.user_logs import (
    get_user_log_list, format_user_logs)
from app.domains.logger.logger_utils.log_utils import (
    create_excel_file, download_excel_file)


user_log_bp = Blueprint(
    "user_log",
    __name__,
    url_prefix="/user_log",
    template_folder="../templates",
    static_folder="../static"
)

@user_log_bp.route("/user_log_list")
def user_log_list():

    logs = get_user_log_list()

    return render_template(
        "user_log_list.html",
        logs = logs)


@user_log_bp.route("/export_user_data")
def export_user_data():

    logs = get_user_log_list()

    cleand_logs = format_user_logs(logs)

    output = create_excel_file(
        cleand_logs, 
        sheet_name="User_Logs")

    return download_excel_file(
        output, 
        "user_logs.xlsx")

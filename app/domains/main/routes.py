import os
from flask import Blueprint, render_template, request
from app.domains.account.validate.validate import login

current_dir = os.path.dirname(os.path.abspath(__file__))

main_bp = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/main/static",
)


@main_bp.route("/")
def main():
    return render_template("main_index.html")


@main_bp.route("/login", methods=["POST"])
def login_result():

    print("🔥 LOGIN ROUTE HIT")  # 이거 추가

    success, message = login(
        request.form["uId"],
        request.form["uPw"]
    )

    print(success, message)

    return render_template(
        "first_login_form.html",
        message=message,
        success=success
    )

@main_bp.route("/first_login_form")
def first_login_form():

    return render_template(
        "first_login_form.html"
    )
    
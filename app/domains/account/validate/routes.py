from flask import Flask, render_template, request

from app.domains.account.validate.routes import register_user, load_accounts, save_accounts

validate_bp = Blueprint(
    "validate",
    __name__,
    url_prefix="/validate",
    template_folder="templates"
)


@validate_bp.route("/")
def index():
    return render_template("validate.html")

@validate_bp.route("validate/signup", methods=["POST"])
def signup():

    accounts = load_accounts()

    user_id = request.form["id"]
    pw = request.form["pw"]
    email = request.form["email"]
    p1 = request.form["p1"]
    p2 = request.form["p2"]
    p3 = request.form["p3"]

    success, message = register_user(
        accounts,
        user_id,
        pw,
        email,
        p1,
        p2,
        p3,
    )

    saved_accounts = load_accounts()

    if user_id in save_accounts:
        print("✅ JSON 저장 성공")
        print(save_accounts[user_id])
    else:
        print("❌ JSON 저장 실패")

    return render_template(
        "validate.html",
        message=message
    )


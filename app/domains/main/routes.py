import os
from flask import Blueprint, render_template, request, session, send_file, redirect, url_for
from app.domains.account.validate.validate import login, change_password, make_captcha, load_accounts
from app import configs

from flask import session

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

    print("main() 실행")

    session.clear()

    session["login_fail"] = 0

    print("초기화 후 :", session["login_fail"])

    return render_template("main_index.html")


@main_bp.route("/login", methods=["POST"])
def login_result():

    success, message = login(
        request.form["uId"],
        request.form["uPw"],
        request.form.get("captcha","")
    )

     

    if success:
        session["login_fail"] = 0
        session["id"] = request.form["uId"]

        accounts = load_accounts()
        user = load_accounts()[session["id"]]

        # 최초 로그인
        if user[configs.KEY_IS_FIRST_LOGIN]:
            return render_template("first_login_form.html")

        # 일반 로그인
        return redirect(url_for("member.member_list"))


    # 로그인 실패 → 실패 횟수 증가
    session["login_fail"] = session.get("login_fail", 0) + 1
    fail_count = session["login_fail"]

    if message == "없는 회원입니다.":
        message = f"없는 회원입니다. ({fail_count}/5)"

    elif message == "비밀번호가 틀렸습니다.":
        message = f"비밀번호가 틀렸습니다. ({fail_count}/5)"

    # 5회 이상 실패하면 CAPTCHA 생성
    if session["login_fail"] >= 5:
        make_captcha()

    return render_template(
    "main_index.html",
    message=message,
    success=False
)
    
@main_bp.route("/first_login_form", methods=["POST"])
def first_login_form():

    success, message = change_password(
        session["id"],                 # 로그인한 사용자 아이디
        request.form["oPw"],           # 현재 임시 비밀번호
        request.form["nPw"],           # 새 비밀번호
        request.form["nPwCheck"]       # 새 비밀번호 확인
    )

    if success: 
        return render_template(
            "main_index.html",
            message=message,
            success=success
        )

    return render_template(
        "first_login_form.html",
        message=message,
        success=success
    )
   



    
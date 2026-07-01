from flask import Blueprint, render_template, request, session, redirect, url_for

# 계정 관련 기능 모듈 import
from app.domains.account.validate.validate import (
    login,                 # 로그인 검증
    change_password,       # 최초 로그인 비밀번호 변경
    create_login_session,  # 로그인 성공 시 Session 생성
    is_first_login,        # 최초 로그인 여부 확인
    login_fail,             # 로그인 실패 처리
    make_captcha
)

from app import configs


# ==========================================================
# Main Blueprint 생성
# 메인 화면과 로그인 관련 URL을 관리
# ==========================================================
main_bp = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/main/static",
)


# ==========================================================
# 메인 로그인 페이지
# ==========================================================
@main_bp.route("/")
def main():

    print("main() 실행")

    # 기존 로그인 정보(Session) 삭제
    # 로그인 화면으로 진입할 때마다 로그아웃된 상태로 시작
    session.clear()

    # 로그인 실패 횟수 초기화
    # CAPTCHA 판단 기준으로 사용
    session["login_fail"] = 0

    print("초기화 후 :", session["login_fail"])

    # 로그인 화면 출력
    return render_template("main_index.html")


# ==========================================================
# 로그인 처리
# ==========================================================
@main_bp.route("/login", methods=["POST"])
def login_result():

    success, message, user = login(
        request.form["uId"],
        request.form["uPw"],
        request.form.get("captcha", "")
    )

    # =====================
    # 성공
    # =====================
    if success:
        create_login_session(request.form["uId"], user)

        if is_first_login(user):
            return render_template("first_login_form.html")

        return redirect(url_for("member.member_list"))

    # =====================
    # 일반 실패 (로그인)
    # =====================
    if message in ("없는 회원입니다.", "비밀번호가 틀렸습니다."):

        fail, message = login_fail(message)

        message = f"{message} ({fail}/{configs.LOGIN_FAIL_LIMIT})"

        # ✔ 딱 3일 때만 CAPTCHA 생성
        if fail == configs.LOGIN_FAIL_LIMIT:
            make_captcha()
            message = "비밀번호 3회 실패로 자동입력 방지가 활성화되었습니다."

    # =====================
    # CAPTCHA 실패 메시지는 그대로 출력
    # =====================
    return render_template("main_index.html", message=message, success=False)

# ==========================================================
# 최초 로그인 비밀번호 변경
# ==========================================================
@main_bp.route("/first_login_form", methods=["POST"])
def first_login_form():

    # 비밀번호 변경 수행
    success, message = change_password(

        # 현재 로그인한 사용자 ID(Session)
        session["id"],

        # 기존(임시) 비밀번호
        request.form["oPw"],

        # 새 비밀번호
        request.form["nPw"],

        # 새 비밀번호 확인
        request.form["nPwCheck"]
    )

    # ======================================================
    # 비밀번호 변경 성공
    # ======================================================
    if success:

        # 로그인 페이지로 이동
        # 변경 완료 메시지 출력
        return render_template(
            "main_index.html",
            message=message,
            success=True
        )

    # ======================================================
    # 비밀번호 변경 실패
    # ======================================================

    # 다시 최초 로그인 화면 출력
    # 실패 사유(message) 표시
    return render_template(
        "first_login_form.html",
        message=message,
        success=False
    )
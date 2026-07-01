from app.utils.time_stamper import get_current_time_stamp_formated
from captcha.image import ImageCaptcha
from flask import session
from app.utils import json_manager
from app import configs

import random
import string


# ==========================================================
# 계정(JSON) 파일 불러오기
# ==========================================================
def load_accounts():
    return json_manager.load_json(json_manager.ACCOUNT_FILE)


# ==========================================================
# 계정(JSON) 파일 저장하기
# ==========================================================
def save_accounts(accounts):
    return json_manager.save_json(json_manager.ACCOUNT_FILE, accounts)


"""
ACNT-003
ID 유효성 검사
ID는 반드시 유일한 값이어야 하며 수정 불가능
"""


# ==========================================================
# 아이디 존재 여부 확인
#
# True  : 존재
# False : 존재하지 않음
# ==========================================================
def is_id_exists(accounts, id):
    return id in accounts


# ==========================================================
# 비밀번호 일치 여부 확인
#
# 아이디가 존재하고
# 입력한 비밀번호가 저장된 비밀번호와 같으면 True
# ==========================================================
def is_pw_correct(accounts, id, pw):
    return (
        is_id_exists(accounts, id)
        and accounts[id][configs.KEY_PW] == pw
    )


# ==========================================================
# 계정 승인 여부 확인
#
# True  : 승인
# False : 승인 대기
# ==========================================================
def is_account_approve(accounts, id):
    return accounts[id][configs.KEY_IS_APPROVE]


# ==========================================================
# 삭제된 아이디 목록 불러오기
# ==========================================================
def load_deleted_ids():
    return json_manager.load_json(configs.DELETED_ID_FILE)


# ==========================================================
# 삭제된 아이디 목록 저장하기
# ==========================================================
def save_deleted_ids(deleted_ids):
    json_manager.save_json(
        configs.DELETED_ID_FILE,
        deleted_ids
    )


"""
ACNT-004
비밀번호 유효성 검사

- 8자 이상
- 특수문자 1개 이상 포함
"""


# ==========================================================
# 비밀번호 규칙 검사
# ==========================================================
def is_password_valid(pw):

    # 최소 길이 검사
    if len(pw) < configs.PASSWORD_MIN_LENGTH:
        return False

    # 특수문자가 하나라도 있으면 True
    for ch in pw:
        if ch in string.punctuation:
            return True

    return False


"""
ACNT-005
이메일 유효성 검사

- @ 포함
- 허용된 도메인만 가능
"""


# ==========================================================
# 이메일 형식 검사
# ==========================================================
def is_email_valid(email):

    # @가 없으면 실패
    if "@" not in email:
        return False

    # gmail.com
    # naver.com
    # daum.net
    domain = email.split("@")[1]

    # 허용된 도메인인지 확인
    if domain not in configs.ALLOW_EMAIL_DOMAINS:
        return False

    return True


"""
ACNT-006
전화번호 유효성 검사

- 숫자만 입력
- 하이픈 제거
- 3 / 4 / 4 자리
"""


# ==========================================================
# 전화번호 검사
# ==========================================================
def is_phone_valid(p1, p2, p3):

    # 혹시 입력된 '-' 제거
    p1 = p1.replace("-", "").strip()
    p2 = p2.replace("-", "").strip()
    p3 = p3.replace("-", "").strip()

    # 숫자인지 확인
    if not (
        p1.isdigit()
        and p2.isdigit()
        and p3.isdigit()
    ):
        return False, "숫자만 입력 가능합니다."

    # 자리수 검사
    if len(p1) != 3 or len(p2) != 4 or len(p3) != 4:
        return False, "전화번호 형식이 올바르지 않습니다."

    # 하나의 문자열로 합치기
    full_phone = p1 + p2 + p3

    return True, full_phone


"""
ACNT-007
회원가입
"""


# ==========================================================
# 계정 생성
#
# 회원가입 성공 시 JSON에 저장될
# 사용자 정보를 생성
# ==========================================================
def create_account(accounts, name, id, pw, email, phone):

    accounts[id] = {

        configs.KEY_NAME: name,
        configs.KEY_ID: id,
        configs.KEY_PW: pw,
        configs.KEY_EMAIL: email,
        configs.KEY_PHONE: phone,

        # 생성 날짜
        configs.KEY_REG_DATE:
            get_current_time_stamp_formated(),

        # 수정 날짜
        configs.KEY_MOT_DATE:
            get_current_time_stamp_formated(),

        # 관리자 승인 전까지 False
        configs.KEY_IS_APPROVE: False,

        # 최초 로그인 여부
        configs.KEY_IS_FIRST_LOGIN: True,

        # 권한 목록
        configs.KEY_PERMISSIONS: [],

        # 상급 관리자
        configs.KEY_SENIOR_ID: "master",
    }


# ==========================================================
# 회원가입 처리
# ==========================================================
def register_user(accounts, name, id, pw, email, p1, p2, p3):

    # 아이디 중복 검사
    if is_id_exists(accounts, id):
        return False, "이미 존재하는 아이디입니다."

    # 삭제된 아이디 재사용 방지
    deleted_ids = load_deleted_ids()

    if id in deleted_ids:
        return False, "삭제된 ID는 사용할 수 없습니다."

    # 비밀번호 검사
    if not is_password_valid(pw):
        return False, "비밀번호는 8자 이상이며 특수문자를 포함해야 합니다."

    # 이메일 검사
    if not is_email_valid(email):
        return False, "올바른 이메일 형식이 아닙니다."

    # 전화번호 검사
    phone_success, validated_phone = is_phone_valid(
        p1,
        p2,
        p3
    )

    if not phone_success:
        return False, validated_phone

    # 계정 생성
    create_account(
        accounts,
        name,
        id,
        pw,
        email,
        validated_phone
    )

    # JSON 저장
    save_accounts(accounts)

    return True, "회원가입이 완료되었습니다."


"""
ACNT-008
로그인
"""


# ==========================================================
# 로그인 검증
# ==========================================================
def login(id, pw, captcha=""):

    accounts = load_accounts()

    login_fail = session.get("login_fail", 0)
    captcha_fail = session.get("captcha_fail", 0)

    # =========================
    # 1. CAPTCHA 상태
    # =========================
    if login_fail >= configs.LOGIN_FAIL_LIMIT:

        # 캡차 틀림
        if captcha != session.get("captcha", ""):

            captcha_fail += 1
            session["captcha_fail"] = captcha_fail

            if captcha_fail >= configs.LOGIN_FAIL_LIMIT:
                return False, "자동입력 방지를 3회 실패하여 계정이 비활성화되었습니다.", None

            return False, f"자동문자 입력이 틀렸습니다 ({captcha_fail}/3)", None

        # 캡차 성공 시 로그인 다시 시도 가능
        return False, "CAPTCHA 확인 후 다시 로그인하세요.", None

    # =========================
    # 2. 일반 로그인
    # =========================
    if id not in accounts:
        return False, "없는 회원입니다.", None

    if accounts[id][configs.KEY_PW] != pw:
        return False, "비밀번호가 틀렸습니다.", None

    if not accounts[id][configs.KEY_IS_APPROVE]:
        return False, "관리자 승인 대기 중입니다.", None

    # 성공
    session["login_fail"] = 0
    session["captcha_fail"] = 0

    return True, "로그인 성공", accounts[id]

"""
ACNT-009
정보 수정 승인
"""


# ==========================================================
# 수정 요청 승인
# ==========================================================
def approve_update(accounts, id):

    if "REQUEST_UPDATE" not in accounts[id]:
        return False, "수정 요청이 없습니다."

    request = accounts[id]["REQUEST_UPDATE"]

    accounts[id][configs.KEY_PW] = request[configs.KEY_PW]
    accounts[id][configs.KEY_EMAIL] = request[configs.KEY_EMAIL]
    accounts[id][configs.KEY_PHONE] = request[configs.KEY_PHONE]

    # 수정 요청 삭제
    del accounts[id]["REQUEST_UPDATE"]

    save_accounts(accounts)

    return True, "정보 수정이 완료되었습니다."


# ==========================================================
# 계정 삭제
#
# 삭제된 ID는 따로 저장하여
# 재사용을 막는다.
# ==========================================================
def delete_account(accounts, id):

    if not is_id_exists(accounts, id):
        return False, "존재하지 않는 계정입니다."

    deleted_ids = load_deleted_ids()

    if id not in deleted_ids:
        deleted_ids.append(id)

    save_deleted_ids(deleted_ids)

    del accounts[id]

    save_accounts(accounts)

    return True, "계정이 삭제되었습니다."


# ==========================================================
# 최초 로그인 비밀번호 변경
# ==========================================================
def change_password(id, oPw, nPw, new_pw_check):

    accounts = load_accounts()

    # 아이디 존재 여부
    if id not in accounts:
        return False, "없는 회원입니다."

    # 현재 비밀번호 확인
    if accounts[id][configs.KEY_PW] != oPw:
        return False, "현재 임시 비밀번호가 일치하지 않습니다."

    # 새 비밀번호 확인
    if nPw != new_pw_check:
        return False, "새 비밀번호가 서로 일치하지 않습니다."

    # 새 비밀번호 규칙 검사
    if not is_password_valid(nPw):
        return False, "비밀번호는 8자 이상이며 특수문자를 포함해야 합니다."

    # 기존 비밀번호와 동일한지 확인
    if oPw == nPw:
        return False, "기존 비밀번호와 다르게 설정해야 합니다."

    # 비밀번호 변경
    accounts[id][configs.KEY_PW] = nPw

    # 최초 로그인 해제
    accounts[id][configs.KEY_IS_FIRST_LOGIN] = False

    # 수정 날짜 변경
    accounts[id][configs.KEY_MOT_DATE] = (
        get_current_time_stamp_formated()
    )

    # 저장
    save_accounts(accounts)

    return True, "비밀번호가 변경되었습니다."


# ==========================================================
# CAPTCHA 생성
#
# 로그인 실패 횟수 초과 시 호출
# ==========================================================
def make_captcha():

    text = ""

    # 랜덤 문자열 생성
    for _ in range(configs.CAPTCHA_LENGTH):
        text += random.choice(
            string.ascii_uppercase +
            string.digits
        )

    # Session 저장
    session["captcha"] = text

    # 이미지 생성
    image = ImageCaptcha()

    image.write(
        text,
        "app/static/captcha.png"
    )


# ==========================================================
# 로그인 Session 생성
#
# 로그인 성공 후 필요한 정보를 저장
# ==========================================================
def create_login_session(user_id, user):

    session["login_fail"] = 0
    session["captcha_fail"] = 0

    session["id"] = user_id
    session["is_approve"] = user[configs.KEY_IS_APPROVE]
    session["is_first_login"] = user[configs.KEY_IS_FIRST_LOGIN]


# ==========================================================
# 최초 로그인 여부 확인
# ==========================================================
def is_first_login(user):
    return user[configs.KEY_IS_FIRST_LOGIN]


# ==========================================================
# 로그인 실패 처리
#
# - 실패 횟수 증가
# - 실패 메시지 변경
# - CAPTCHA 생성
# ==========================================================
def login_fail(message):

    fail = session.get("login_fail", 0)

    # ✔ 증가는 여기서만
    if fail < configs.LOGIN_FAIL_LIMIT:
        fail += 1
        session["login_fail"] = fail

    return fail, message
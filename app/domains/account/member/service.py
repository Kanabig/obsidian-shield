from app.utils.time_stamper import get_current_time_stamp_formated
from app import configs
from app.utils.account_manager import load_accounts
from flask import session   
from app.domains.account.permissions import PERMISSON
from app.domains.account.permissions import ADMIN, OBSERVER

def make_member(member_data):

    now = get_current_time_stamp_formated()

    if member_data["permission"] == "ADMIN":
        permissions = [perm.value for perm in ADMIN]
    else:
        permissions = [perm.value for perm in OBSERVER]

    return {
        configs.KEY_ID: member_data["id"],
        configs.KEY_PW: member_data["pw"],
        configs.KEY_NAME: member_data["name"],
        configs.KEY_PHONE: member_data["phone"],
        configs.KEY_EMAIL: member_data["email"],
        configs.KEY_PERMISSIONS: permissions,
        configs.KEY_IS_APPROVE: member_data["approve"] == "승인",
        configs.KEY_IS_FIRST_LOGIN: True,
        configs.KEY_REG_DATE: now,
        configs.KEY_MOD_DATE: now
    }

def update_member(account_db, member_id, permission, approve):

    
    if not is_admin(session["id"]):
        return False, "권한이 없습니다."

    # 역할에 따라 권한 저장
    if permission == "ADMIN":
        account_db[member_id][configs.KEY_PERMISSIONS] = [
            perm.value for perm in ADMIN
        ]
    else:
        account_db[member_id][configs.KEY_PERMISSIONS] = [
            perm.value for perm in OBSERVER
        ]

    account_db[member_id][configs.KEY_IS_APPROVE] = approve == "승인"
    account_db[member_id][configs.KEY_MOD_DATE] = get_current_time_stamp_formated()

    return True, "수정 완료"


def delete_member(account_db, member_id):

    if member_id in account_db:
        del account_db[member_id]


def is_admin(user_id):
    accounts = load_accounts()

    return (
        PERMISSON.MEMBER_ACCESS.value
        in accounts[user_id][configs.KEY_PERMISSIONS]
    )

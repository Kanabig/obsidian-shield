from app.utils.time_stamper import get_current_time_stamp_formated

def make_member(
    member_id,
    password,
    name,
    phone,
    email,
    permission,
    approve
):

    now = get_current_time_stamp_formated()

    return {
        "ID": member_id,
        "PASSWORD": password,
        "NAME": name,
        "PHONE": phone,
        "EMAIL": email,
        "PERMISSIONS": [permission],
        "IS_APPROVE": approve == "승인",
        "REG_DATE": now,
        "MOD_DATE": now
    }


def update_member(account_db, member_id, permission, approve):

    account_db[member_id]["PERMISSIONS"] = [permission]
    account_db[member_id]["IS_APPROVE"] = approve == "승인"
    account_db[member_id]["MOD_DATE"] = get_current_time_stamp_formated()


def delete_member(account_db, member_id):

    if member_id in account_db:
        del account_db[member_id]

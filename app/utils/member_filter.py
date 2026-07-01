def filter_keyword(accounts, keyword, tag):

    if not keyword:
        return accounts

    keyword = keyword.lower()

    if tag == "아이디":
        return [a for a in accounts if keyword in a.get("ID", "").lower()]

    elif tag == "이름":
        return [a for a in accounts if keyword in a.get("NAME", "").lower()]

    elif tag == "역할":
        return [a for a in accounts if keyword in ",".join(a.get("PERMISSIONS", [])).lower()]

    return [
        a for a in accounts
        if keyword in a.get("ID", "").lower()
        or keyword in a.get("NAME", "").lower()
        or keyword in ",".join(a.get("PERMISSIONS", [])).lower()
    ]


def filter_permission(accounts, permission):

    if permission == "전체":
        return accounts

    return [a for a in accounts if permission in a.get("PERMISSIONS", [])]


def filter_approve(accounts, approve):

    if approve == "승인":
        return [a for a in accounts if a.get("IS_APPROVE") is True]

    elif approve == "미승인":
        return [a for a in accounts if a.get("IS_APPROVE") is False]

    return accounts
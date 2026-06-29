import os
import json
import math
from app.utils.json_manager import ACCOUNT_FILE
from flask import Blueprint, render_template, request

member_bp = Blueprint(
    "member", __name__, template_folder="templates", static_folder="static", static_url_path="/member/static"
)


@member_bp.route("/member/list")
def member_list():

    with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
        account_db = json.load(f)

    accounts = list(account_db.values())

    keyword = request.args.get("keyword", "").strip()
    tag = request.args.get("tag", "전체")
    permission = request.args.get("permission", "전체")
    approve = request.args.get("approve", "전체")
    sort = request.args.get("sort", "최신등록순")
    per_page = int(request.args.get("per_page", 10))
    page = int(request.args.get("page", 1))

    # 검색
    if keyword:
        if tag == "아이디":
            accounts = [a for a in accounts if keyword.lower() in a.get("ID", "").lower()]
        elif tag == "이름":
            accounts = [a for a in accounts if keyword.lower() in a.get("NAME", "").lower()]
        elif tag == "역할":
            accounts = [
                a for a in accounts
                if keyword in ",".join(a.get("PERMISSIONS", []))
            ]
        else:
            accounts = [
                a for a in accounts
                if keyword.lower() in a.get("ID", "").lower()
                or keyword.lower() in a.get("NAME", "").lower()
                or keyword in ",".join(a.get("PERMISSIONS", []))
            ]

    # 권한 필터
    if permission != "전체":
        accounts = [
            a for a in accounts
            if permission in a.get("PERMISSIONS", [])
        ]

    # 승인 필터
    if approve == "승인":
        accounts = [a for a in accounts if a.get("IS_APPROVE") is True]
    elif approve == "미승인":
        accounts = [a for a in accounts if a.get("IS_APPROVE") is False]

    # 정렬
    if sort == "최신등록순":
        accounts.sort(key=lambda a: a.get("REG_DATE", ""), reverse=True)
    elif sort == "오래된순":
        accounts.sort(key=lambda a: a.get("REG_DATE", ""))
    elif sort == "아이디순":
        accounts.sort(key=lambda a: a.get("ID", ""))
    elif sort == "이름순":
        accounts.sort(key=lambda a: a.get("NAME", ""))

    # 페이지네이션
    total_count = len(accounts)
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1

    start = (page - 1) * per_page
    end = start + per_page
    accounts = accounts[start:end]

    return render_template(
        "member_list.html",
        account_db=accounts,
        keyword=keyword,
        tag=tag,
        permission=permission,
        approve=approve,
        sort=sort,
        per_page=per_page,
        page=page,
        total_pages=total_pages
    )
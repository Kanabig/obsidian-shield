from flask import Blueprint, render_template, request, redirect
from app.utils.account_manager import load_accounts, save_accounts
from .service import (make_member, update_member, delete_member)
from app.utils.member_filter import filter_keyword, filter_permission, filter_approve
from app.utils.member_sort import sort_accounts
from app.utils.pagination import paginate

member_bp = Blueprint(
    "member", __name__, template_folder="templates", static_folder="static", static_url_path="/member/static"
)

@member_bp.route("/member/update/<member_id>", methods=["POST"])
def member_update(member_id):

    account_db = load_accounts()

    permission = request.form.get("permission")
    approve = request.form.get("approve")

    if member_id in account_db:
        update_member(account_db, member_id, permission, approve)
        save_accounts(account_db)

    return redirect("/member/list")

@member_bp.route("/member/list")
def member_list():

    account_db = load_accounts()

    accounts = list(account_db.values())

    keyword = request.args.get("keyword", "").strip()
    tag = request.args.get("tag", "전체")
    permission = request.args.get("permission", "전체")
    approve = request.args.get("approve", "전체")
    sort = request.args.get("sort", "최신등록순")
    per_page = int(request.args.get("per_page", 10))
    page = int(request.args.get("page", 1))
    edit_id = request.args.get("edit_id", "")
    mode = request.args.get("mode", "list")

    # 검색
    accounts = filter_keyword(accounts, keyword, tag)
    accounts = filter_permission(accounts, permission)
    accounts = filter_approve(accounts, approve)

    # 정렬
    accounts = sort_accounts(accounts, sort)

    # 페이지네이션
    accounts, total_pages = paginate(accounts, page, per_page)

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
        total_pages=total_pages,
        edit_id=edit_id,
        mode=mode
    )

@member_bp.route("/member/add", methods=["POST"])
def member_add():

    account_db = load_accounts()

    member_id = request.form.get("id", "").strip()
    password = request.form.get("pw", "").strip()
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    permission = request.form.get("permission", "관제자")
    approve = request.form.get("approve", "미승인")

    if member_id in account_db:
        return """
        <script>
            alert('이미 존재하는 아이디입니다.');
            history.back();
        </script>
        """

    account_db[member_id] = make_member(member_id, password, name, phone, email, permission, approve)

    save_accounts(account_db)

    return redirect("/member/list")

@member_bp.route("/member/delete/<member_id>")
def member_delete(member_id):

    account_db = load_accounts()

    delete_member(account_db, member_id)
    save_accounts(account_db)

    return redirect("/member/list")
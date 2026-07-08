from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.account_manager import load_accounts, save_accounts
from .service import make_member, update_member, delete_member, is_admin
from .request_data import get_member_list_options, get_member_add_data, get_member_update_data
from app.utils.member_filter import filter_keyword, filter_permission, filter_approve
from app.utils.member_sort import sort_accounts
from app.utils.pagination import paginate
from app.domains.account.validate.validate import validate_register
from app import configs
from app.domains.account.permissions import PERMISSON

member_bp = Blueprint(
    "member", __name__, template_folder="templates", static_folder="static", static_url_path="/member/static"
)

@member_bp.route("/member/update/<member_id>", methods=["POST"])
def member_update(member_id):

    account_db = load_accounts()

    member_data = get_member_update_data(request)

    success, message = update_member(
    account_db,
    member_id,
    member_data["permission"],
    member_data["approve"]
    )
    
    if not success:
        return f"""
        <script>
        alert("{message}");
        history.back();
        </script>
        """
    
    save_accounts(account_db)


    return redirect("/member/list")

@member_bp.route("/member/list")
def member_list():


    # 로그인 안 했으면 로그인 화면으로
    if "id" not in session:
        return redirect(url_for("main.main"))

    account_db = load_accounts()

    accounts = list(account_db.values())

  
    for account in accounts:

        permissions = account[configs.KEY_PERMISSIONS]

        if PERMISSON.MEMBER_ACCESS.value in permissions:
            account["PERMISSION_NAME"] = "관리자"
        else:
            account["PERMISSION_NAME"] = "관제자"

    options = get_member_list_options(request)

    # 검색
    accounts = filter_keyword(accounts, options["keyword"], options["tag"])
    accounts = filter_permission(accounts, options["permission"])
    accounts = filter_approve(accounts, options["approve"])

    # 정렬
    accounts = sort_accounts(accounts, options["sort"])

    # 페이지네이션
    accounts, total_pages = paginate(accounts, options["page"], options["per_page"])

    if PERMISSON.MEMBER_ACCESS.value in session["permissions"]:
        user_permission = "관리자"
    else:
        user_permission = "관제자"


    return render_template(
        "member_list.html",
        user_permission=user_permission,
        user_id=session["id"],   
        account_db=accounts,
        keyword=options["keyword"],
        tag=options["tag"],
        permission=options["permission"],
        approve=options["approve"],
        sort=options["sort"],
        per_page=options["per_page"],
        page=options["page"],
        total_pages=total_pages,
        edit_id=options["edit_id"],
        mode=options["mode"]
    )

@member_bp.route("/member/add", methods=["POST"])
def member_add():

    account_db = load_accounts()

    if not is_admin(session["id"]):
        return """
        <script>
        alert("권한이 없습니다.");
        history.back();
        </script>
        """

    member_data = get_member_add_data(request)

    success, field, message, phone = validate_register(
        account_db,
        member_data["id"],
        member_data["pw"],
        member_data["email"],
        member_data["phone1"],
        member_data["phone2"],
        member_data["phone3"]
    )

    if not success:

        return render_template(
            "member_list.html",
            error_field=field,
            error_message=message,
            member_data=member_data
        )
    
    member_data["phone"] = phone
    
    account_db[member_data["id"]] = make_member(member_data)

    save_accounts(account_db)

    return redirect("/member/list")

@member_bp.route("/member/delete/<member_id>")
def member_delete(member_id):

    account_db = load_accounts()

    if not is_admin(session["id"]):
        return """
        <script>
        alert("권한이 없습니다.");
        history.back();
        </script>
        """

    delete_member(account_db, member_id)
    save_accounts(account_db)

    return redirect("/member/list")
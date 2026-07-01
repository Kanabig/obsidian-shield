def sort_accounts(accounts, sort):

    if sort == "최신등록순":
        accounts.sort(
            key=lambda a: a.get("REG_DATE", ""),
            reverse=True
        )

    elif sort == "오래된순":
        accounts.sort(
            key=lambda a: a.get("REG_DATE", "")
        )

    elif sort == "아이디순":
        accounts.sort(
            key=lambda a: a.get("ID", "")
        )

    elif sort == "이름순":
        accounts.sort(
            key=lambda a: a.get("NAME", "")
        )

    return accounts
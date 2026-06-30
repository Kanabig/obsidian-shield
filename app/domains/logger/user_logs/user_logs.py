from app.utils.json_manager import (
    load_json, save_json, USER_LOGS_FILE)


def get_user_log_list():

    logs = load_json(USER_LOGS_FILE)

    return list(logs.values())


def add_user(data):
    logs = load_json(USER_LOGS_FILE)

    logs[data["ID"]] = {
        "EVENT_LOG_ID" : data["EVENT_LOG_ID"],
        "VIEWER_ID" : data["VIEWER_ID"],
        "IS_CHECKED" : data["IS_CHECKED"]
    }

    save_json(USER_LOGS_FILE, logs)


def check_user_log(user_log_id):
    logs = load_json(USER_LOGS_FILE)

    if user_log_id in logs:
        logs[user_log_id]["IS_CHECKED"] = True
        save_json(USER_LOGS_FILE, logs)


def format_user_logs(user_logs):
    cleaned_user_logs = []

    for user_log in user_logs:
        cleaned_user_logs.append(
            {
                "이벤트ID": user_log.get("EVENT_LOG_ID"),
                "사용자": user_log.get("VIEWER_ID"),
                "확인여부": user_log.get("IS_CHECKED")
            }
        )

    return cleaned_user_logs


if __name__ == "__main__":
    user_logs = get_user_log_list()

    for user_log in user_logs:
        print(user_log)

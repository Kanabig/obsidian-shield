from app.utils.time_stamper import (
    get_current_time_stamp_formated)
from app.utils.json_manager import (
    load_json, save_json, EVENT_LOGS_FILE, 
    USER_LOGS_FILE)
from app.domains.logger.logger_utils.event_notifier import (
    notify_new_log)
from app.domains.logger.user_logs.user_logs import (
    add_user_log)


# ===========================================================
# 이벤트 로그 전체 조회
# ===========================================================
def get_event_list():

    logs = load_json(EVENT_LOGS_FILE)

    events = list(logs.values())

    events.sort(
        key = lambda x: x["REG_DATE"],
        reverse = True
    )

    return events


# ===========================================================
# 새로운 이벤트 저장
# ===========================================================
def add_event(data):

    logs = load_json(EVENT_LOGS_FILE)

    logs[data["ID"]] = {
        "ID": data["ID"],
        "REG_DATE": get_current_time_stamp_formated(),
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "TARGET_ID": data["TARGET_ID"],
        "IS_READ": False
    }

    save_json(EVENT_LOGS_FILE, logs)

    print("로그 저장 완료")

    notify_new_log()

    print("notify_new_log 호출")


# ===========================================================
# 마지막으로 받은 로그 이후의 로그 반환
# ===========================================================
def get_new_event_list(after_id):

    events = get_event_list()

    if after_id is None:
        return events
    
    new_events = []

    for event in events:

        if event["ID"] == after_id:
            break

        new_events.append(event)

    return list(reversed(new_events))

# ===========================================================
# 엑셀 저장용 데이터 변환
# ===========================================================
def format_events(events):

    cleaned_events = []

    for event in events:
        cleaned_events.append({
                "이벤트_ID": event.get("ID"),
                "이벤트_발생시각": event.get("REG_DATE"),
                "이벤트_발생위도": event.get("latitude"),
                "이벤트_발생경도": event.get("longitude"),
                "대상_ID": event.get("TARGET_ID"),
                "이벤트_상태": event.get("IS_READ")
            })
        
    return cleaned_events


# ===========================================================
# 이벤트 읽음 처리
# ===========================================================
def checked_event_logs(event_ids, viewer_id):

    events = load_json(EVENT_LOGS_FILE)

    for event_id in event_ids:

        if event_id not in events:
            continue

        if events[event_id]["IS_READ"]:
            continue

        events[event_id]["IS_READ"] = True

    add_user_log(event_id, viewer_id)

    save_json(EVENT_LOGS_FILE, events)


if __name__ == "__main__":
    events = get_event_list()

    for event in events:
        print(event)
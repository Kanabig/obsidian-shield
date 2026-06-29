from app.utils.json_manager import load_json, save_json
from app.utils.time_stamper import get_current_time_stamp_formated
from app.utils.json_manager import EVENT_LOGS_FILE

def get_event_list():

    logs = load_json(EVENT_LOGS_FILE)

    return list(logs.values())


def add_event(data):

    logs = load_json(EVENT_LOGS_FILE)

    logs[data["ID"]] = {
        "ID": data["ID"],
        "REG_DATE": get_current_time_stamp_formated(),
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "TARGET_ID": data["TARGET_ID"]
    }

    save_json(EVENT_LOGS_FILE, logs)


if __name__ == "__main__":
    events = get_event_list()

    for event in events:
        print(event)

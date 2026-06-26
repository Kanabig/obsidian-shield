from app.utils.json_manager import load_json

def get_event_list():

    logs = load_json("app/jsons/event_logs.json")

    return list(logs.values())


if __name__ == "__main__":
    events = get_event_list()

    for event in events:
        print(event)
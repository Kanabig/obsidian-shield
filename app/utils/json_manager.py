import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ACCOUNT_FILE = os.path.join(BASE_DIR, "jsons", "accounts.json")
EVENT_LOGS_FILE = os.path.join(BASE_DIR, "jsons", "event_logs.json")
TARGETS_FILE = os.path.join(BASE_DIR, "jsons", "targets_info.json")


def load_json(file):
    try:
        with open(file, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return {}


def save_json(file, json_data):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)

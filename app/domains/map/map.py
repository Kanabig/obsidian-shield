from app.utils.json_manager import (
    load_json, 
    EVENT_LOGS_FILE, 
    TARGETS_PROFILES_FILE
)

def get_map_data():
    event_logs = load_json(EVENT_LOGS_FILE) or {}
    target_profiles = load_json(TARGETS_PROFILES_FILE) or {}
    
    Latest_logs = {}

    for log in event_logs.values():
        target_id = log.get("TARGET_ID")
        if not target_id:
            continue

        if target_id not in Latest_logs:
            Latest_logs[target_id] = log
        else:
            if log["REG_DATE"] > Latest_logs[target_id]["REG_DATE"]:
                Latest_logs[target_id] = log
   
    map_data = []
    
    for target_id, latest_log in Latest_logs.items():
        target = target_profiles.get(target_id)

        if target:
            map_data.append({
                "id" : target["ID"],
                "name": target["NAME"],
                "age" : target["AGE"], 
                "short_description" : target["SHORT_DESCRIPTION"], 
                "description" : target["DESCRIPTION"], 
                "image" : target.get("IMAGE", "temp.jpg"), 
                "latitude" : latest_log["latitude"], 
                "longitude" : latest_log["longitude"],
                "reg_date" : latest_log["REG_DATE"],
            })
    return map_data

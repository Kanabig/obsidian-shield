from app.utils.json_manager import (
    load_json, 
    EVENT_LOGS_FILE, 
    TARGETS_PROFILES_FILE
)
from app import configs
import hashlib

def get_color(target_id):
        
        value = int(hashlib.md5(target_id.encode()).hexdigest(), 16)
        hue = value % 360
        return f"hsl({hue}, 80%, 45%)"

def get_map_data():
    event_logs = load_json(EVENT_LOGS_FILE) or {}
    target_profiles = load_json(TARGETS_PROFILES_FILE) or {}
    
    target_logs = {}
    for log in event_logs.values():
        target_id = log.get("TARGET_ID")
        
        if not target_id:
            continue

        if target_id not in target_logs:
            target_logs[target_id] = []
        
        target_logs[target_id].append(log)
   
    map_data = []
    
    for target_id, logs in target_logs.items():
        logs.sort(key=lambda x: x["REG_DATE"])

        # 최근 로그 n개
        logs = logs[-10:]

        # 가장 마지막 로그 = 현재 위치
        latest_log = logs[-1]

        step = max(1, len(logs) // 5)
        sampled_logs = logs[::step]

        target = target_profiles.get(target_id)

        if sampled_logs[-1] != logs[-1]:
            sampled_logs.append(logs[-1])
    

            map_data.append({
                "id" : target[configs.KEY_ID],
                "name": target[configs.KEY_NAME],
                "age" : target["AGE"], 
                "short_description" : target["SHORT_DESCRIPTION"], 
                "description" : target["DESCRIPTION"], 
                "image" : target.get("IMAGE"), 
                
                #target 별 line색상
                "color": get_color(target["ID"]),
                
                #현재위치
                "latitude" : latest_log["latitude"], 
                "longitude" : latest_log["longitude"],
                
                #이동 경로
                "logs": sampled_logs,
                
                #등록 일시
                "reg_date" : latest_log["REG_DATE"],
            })
    return map_data

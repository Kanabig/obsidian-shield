from app.utils.json_manager import (
    load_json, 
    EVENT_LOGS_FILE, 
    TARGETS_PROFILES_FILE
)

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
        
        # 가장 마지막 로그 = 현재 위치
        latest_log = logs[-1]

        target = target_profiles.get(target_id)

        count = len(logs)

        sampled_logs = [
            logs[0],
            logs[count // 4],
            logs[count // 2],
            logs[(count * 3) // 4],
            logs[-1]
        ]


        if target:
            color_map = {
                "target_001": "#FF0000",
                "target_002": "#0000FF",
                "target_003": "#00AA00",
                "target_004": "#FFA500"
            }

            map_data.append({
                "id" : target["ID"],
                "name": target["NAME"],
                "age" : target["AGE"], 
                "short_description" : target["SHORT_DESCRIPTION"], 
                "description" : target["DESCRIPTION"], 
                "image" : target.get("IMAGE"), 
                
                #target 별 line색상
                "color": color_map.get(target["ID"],"#808080"),
                
                #현재위치
                "latitude" : latest_log["latitude"], 
                "longitude" : latest_log["longitude"],
                
                #이동 경로
                "logs": sampled_logs,
                
                #등록 일시
                "reg_date" : latest_log["REG_DATE"],
            })
    return map_data

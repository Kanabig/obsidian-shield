from flask import send_file
from app.utils.json_manager import load_json, TARGETS_FILE
import pandas as pd
import io


def format_events(events):
    targets = load_json(TARGETS_FILE)

    cleaned_events = []

    for event in events:

        target_id = event.get("TARGET_ID")
        target = targets.get(target_id, {})

        place_text = f"{event.get('latitude')}, {event.get('longitude')}"
            
        cleaned_events.append(
            {
                "ID": event.get("ID"),
                "시간": event.get("REG_DATE"),
                "장소": place_text,
                "대상ID": target_id
            }
        )
    return cleaned_events


def create_excel_file(cleaned_events):
    data_frame = pd.DataFrame(cleaned_events)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data_frame.to_excel(
            writer,
            index=False,
            sheet_name="Event_Logs"
        )

    output.seek(0)

    return output


def download_excel_file(output):
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="event_logs.xlsx",
    )
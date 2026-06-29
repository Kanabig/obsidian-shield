from flask import send_file
import pandas as pd
import io


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
from flask import Blueprint, render_template, request
from logger.event_logs.event_logs import get_event_list, add_event
from logger.logger_utils.log_utils import (
    format_accounts, create_excel_file, download_excel_file)



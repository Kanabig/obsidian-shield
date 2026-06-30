from flask import Blueprint, render_template, request
from logger.event_logs.user_logs import format_user_account
from logger.logger_utils.log_utils import (
    format_accounts, create_excel_file, download_excel_file)



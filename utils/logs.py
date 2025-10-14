"""
This module sets up the logging configuration for the application.
It configures a rotating file handler and a stream handler for the root logger.
"""

import logging
import os
import shutil
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# مسیر فایل لاگ را تعیین می‌کنیم - از دایرکتوری logs استفاده می‌کنیم
logs_dir = "logs"
log_file_path = os.path.join(logs_dir, "app.log")

# اطمینان از وجود دایرکتوری logs
os.makedirs(logs_dir, exist_ok=True)

# اگر app.log یک دایرکتوری است، آن را حذف می‌کنیم
old_log_path = "app.log"
if os.path.exists(old_log_path) and os.path.isdir(old_log_path):
    try:
        shutil.rmtree(old_log_path)
        print(f"Removed conflicting directory: {old_log_path}")
    except Exception as e:
        print(f"Warning: Could not remove directory {old_log_path}: {e}")

# اگر log_file_path یک دایرکتوری است، آن را حذف می‌کنیم
if os.path.exists(log_file_path) and os.path.isdir(log_file_path):
    try:
        shutil.rmtree(log_file_path)
        print(f"Removed conflicting directory: {log_file_path}")
    except Exception as e:
        print(f"Warning: Could not remove directory {log_file_path}: {e}")
        # از نام فایل جایگزین استفاده می‌کنیم
        log_file_path = os.path.join(logs_dir, "application.log")

file_handler = RotatingFileHandler(
    log_file_path, maxBytes=7 * 10**6, backupCount=3
)  # 7MB per file, keep 3 old files
file_handler.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

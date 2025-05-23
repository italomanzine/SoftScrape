import logging
import os
import sys

CURRENT_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_OUTPUT_PARENT_DIR = CURRENT_MODULE_DIR
OUTPUT_DIR_NAME = "outputs"
ERROR_DIR_NAME = "errors"
ERROR_LOG_FILENAME = "log_errors.txt"

LOG_DIR_PATH = os.path.join(LOG_OUTPUT_PARENT_DIR, OUTPUT_DIR_NAME)
ERROR_LOG_DIR = os.path.join(LOG_DIR_PATH, ERROR_DIR_NAME)
ERROR_LOG_FILE_PATH = os.path.join(ERROR_LOG_DIR, ERROR_LOG_FILENAME)

os.makedirs(ERROR_LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

error_file_handler = logging.FileHandler(ERROR_LOG_FILE_PATH)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

_handlers_configured = False

def get_logger(name: str) -> logging.Logger:
    global _handlers_configured

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not _handlers_configured:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Ensure our specific handlers are on the root logger.
        # The logging module handles duplicates gracefully (won't add if already present).
        if console_handler not in root_logger.handlers:
            root_logger.addHandler(console_handler)
        if error_file_handler not in root_logger.handlers:
            root_logger.addHandler(error_file_handler)
        
        _handlers_configured = True

    return logger

# --- Import the built-in logging module ---
import logging

# --- Import os for handling file paths and directory creation ---
import os

# --- Import handler to enable time-based log rotation ---
from logging.handlers import TimedRotatingFileHandler

# --- Import JSON log formatter from external package ---
from pythonjsonlogger import jsonlogger

# --- Define the directory where logs will be stored ---
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')

# --- Create the logs directory if it doesn't already exist ---
os.makedirs(LOG_DIR, exist_ok=True)

# --- Define the full path for the access log file ---
ACCESS_LOG_PATH = os.path.join(LOG_DIR, 'access.log')

# --- Function to create and return a logger instance ---
def get_logger(name: str = "base_logger") -> logging.Logger:
    # --- Create or get the named logger instance ---
    logger = logging.getLogger(name)

    # --- Set the base logging level to DEBUG (logs all levels) ---
    logger.setLevel(logging.DEBUG)

    # --- Prevent adding multiple handlers if already set ---
    if not logger.handlers:
        # --- Define JSON log formatter with standard fields ---
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )

        # --- Create a rotating file handler for access logs ---
        access_handler = TimedRotatingFileHandler(
            ACCESS_LOG_PATH, when="midnight", interval=1, backupCount=0  # Rotate daily
        )

        # --- Set handler to log INFO and above ---
        access_handler.setLevel(logging.INFO)

        # --- Apply JSON formatter to the handler ---
        access_handler.setFormatter(formatter)

        # --- Add only the access log handler to the logger ---
        logger.addHandler(access_handler)

    # --- Return the configured logger ---
    return logger

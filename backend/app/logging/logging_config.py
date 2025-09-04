# ---------------------------- External Imports ----------------------------
# Built-in logging module for tracking events and errors
import logging

# Built-in os module for handling file paths and directory operations
import os

# Handler for rotating log files based on time intervals
from logging.handlers import TimedRotatingFileHandler

# JSON log formatter from external package for structured logging
from pythonjsonlogger import jsonlogger

# ---------------------------- Log Directory Setup ----------------------------
# Define directory path to store log files
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')

# Create the logs directory if it does not exist
os.makedirs(LOG_DIR, exist_ok=True)

# Define full path for the access log file
ACCESS_LOG_PATH = os.path.join(LOG_DIR, 'access.log')

# ---------------------------- Logger Factory Function ----------------------------
def get_logger(name: str = "base_logger") -> logging.Logger:
    """
    Input:
        1. name (str): Name of the logger (default "base_logger").
    
    Process:
        1. Get or create a logger instance with the specified name.
        2. Set logging level to DEBUG for capturing all logs.
        3. Check if logger already has handlers to avoid duplicates.
        4. Create JSON formatter with standard fields.
        5. Create a timed rotating file handler for access logs.
        6. Set handler level and formatter.
        7. Add handler to logger.
    
    Output:
        1. logging.Logger: Configured logger instance.
    """
    # ---------------------------- Get or Create Logger ----------------------------
    logger = logging.getLogger(name)

    # ---------------------------- Set Logging Level ----------------------------
    logger.setLevel(logging.DEBUG)

    # ---------------------------- Avoid Duplicate Handlers ----------------------------
    if not logger.handlers:
        # ---------------------------- Create JSON Formatter ----------------------------
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )

        # ---------------------------- Create Timed Rotating File Handler ----------------------------
        access_handler = TimedRotatingFileHandler(
            ACCESS_LOG_PATH, when="midnight", interval=1, backupCount=0
        )

        # ---------------------------- Set Handler Level ----------------------------
        access_handler.setLevel(logging.INFO)

        # ---------------------------- Apply Formatter ----------------------------
        access_handler.setFormatter(formatter)

        # ---------------------------- Add Handler to Logger ----------------------------
        logger.addHandler(access_handler)

    # ---------------------------- Return Configured Logger ----------------------------
    return logger

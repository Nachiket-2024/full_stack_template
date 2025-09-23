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
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure logs directory exists

# Define full path for the access log file
ACCESS_LOG_PATH = os.path.join(LOG_DIR, 'access.log')

# ---------------------------- Logger Factory Function ----------------------------
def get_logger(name: str = "base_logger") -> logging.Logger:
    """
    Input:
        1. name (str): Name of the logger (default "base_logger").
    
    Process:
        1. Get or create a logger instance with the specified name.
        2. Set the logger level to DEBUG to capture all log levels.
        3. Avoid duplicate handlers if logger already has handlers.
        4. Create JSON formatter for structured logging.
        5. Create a timed rotating file handler for access logs.
        6. Set the handler level and attach formatter.
        7. Add handler to the logger.
        8. Return the fully configured logger.
    
    Output:
        1. logging.Logger: Fully configured logger instance.
    """
    # Step 1: Get or create a logger instance with the specified name
    logger = logging.getLogger(name)

    # Step 2: Set the logger level to DEBUG to capture all log levels
    logger.setLevel(logging.DEBUG)

    # Step 3: Avoid duplicate handlers if logger already has handlers
    if not logger.handlers:
        # Step 4: Create JSON formatter for structured logging
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )

        # Step 5: Create a timed rotating file handler for access logs
        access_handler = TimedRotatingFileHandler(
            ACCESS_LOG_PATH,  # Path to log file
            when="midnight",  # Rotate logs at midnight
            interval=1,       # Every 1 day
            backupCount=0     # No backup limit
        )

        # Step 6: Set the handler level and attach formatter
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(formatter)

        # Step 7: Add handler to the logger
        logger.addHandler(access_handler)

    # Step 8: Return the fully configured logger
    return logger

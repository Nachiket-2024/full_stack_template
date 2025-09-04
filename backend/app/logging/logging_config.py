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
# Function to create and return a configured logger instance
def get_logger(name: str = "base_logger") -> logging.Logger:
    
    # Get or create a logger with the specified name
    logger = logging.getLogger(name)

    # Set base logging level to DEBUG to capture all log levels
    logger.setLevel(logging.DEBUG)

    # Avoid adding multiple handlers if logger already has them
    if not logger.handlers:
        # Create JSON formatter with standard fields
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )

        # Create a time-based rotating file handler for access logs
        access_handler = TimedRotatingFileHandler(
            ACCESS_LOG_PATH, when="midnight", interval=1, backupCount=0
        )

        # Set handler to log INFO level and above
        access_handler.setLevel(logging.INFO)

        # Apply JSON formatter to the handler
        access_handler.setFormatter(formatter)

        # Add the access log handler to the logger
        logger.addHandler(access_handler)

    # Return the configured logger instance
    return logger

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
        2. Set logging level to DEBUG for capturing all logs.
        3. Check if logger already has handlers to avoid duplicates.
        4. Create JSON formatter with standard fields.
        5. Create a timed rotating file handler for access logs.
        6. Set handler level and formatter.
        7. Add handler to logger.
    
    Output:
        1. logging.Logger: Configured logger instance.
    """
    # Get or create logger instance
    logger = logging.getLogger(name)

    # Set logger to capture all debug and above level logs
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if already present
    if not logger.handlers:
        # Create JSON formatter for structured logging
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )

        # Create a timed rotating file handler for daily log rotation
        access_handler = TimedRotatingFileHandler(
            ACCESS_LOG_PATH,  # Path to log file
            when="midnight",  # Rotate logs at midnight
            interval=1,       # Every 1 day
            backupCount=0     # No backup limit
        )

        # Set logging level for this handler
        access_handler.setLevel(logging.INFO)

        # Attach JSON formatter to handler
        access_handler.setFormatter(formatter)

        # Add handler to logger instance
        logger.addHandler(access_handler)

    # Return the fully configured logger
    return logger

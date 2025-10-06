# ---------------------------- External Imports ----------------------------
# Celery for asynchronous task queue management
from celery import Celery

# ---------------------------- Internal Imports ----------------------------
# Load Celery broker and backend URLs from application settings
from ..core.settings import settings

# Import centralized logger factory to create structured, module-specific loggers
from ..logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Celery App Initialization ----------------------------
# Instantiate Celery with app name, broker, and backend
celery_app = Celery(
    "app_tasks",  # Name of the Celery app
    broker=settings.CELERY_BROKER_URL,  # Broker URL for task queue
    backend=settings.CELERY_RESULT_BACKEND,  # Backend URL for task results
)

# Automatically discover Celery tasks in specified packages
celery_app.autodiscover_tasks(["app.celery.email_tasks"])

# ---------------------------- Celery Configuration ----------------------------
# Update Celery configuration for serialization, timezone, and async pool
celery_app.conf.update(
    task_serializer="json",           # Serialize tasks in JSON format
    result_serializer="json",         # Serialize task results in JSON
    accept_content=["json"],          # Accept only JSON content
    timezone="UTC",                   # Set timezone to UTC
    enable_utc=True,                  # Enable UTC timezone usage
)

# Log successful Celery app initialization
logger.info("Celery app initialized with broker: %s", settings.CELERY_BROKER_URL)

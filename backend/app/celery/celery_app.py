# ---------------------------- External Imports ----------------------------
# Celery for asynchronous task queue management
from celery import Celery

# Logging module for tracking events and errors
import logging

# ---------------------------- Internal Imports ----------------------------
# Load Celery broker and backend URLs from application settings
from ..core.settings import settings

# ---------------------------- Logger Setup ----------------------------
# Create a module-specific logger instance
logger = logging.getLogger(__name__)

# ---------------------------- Celery App Initialization ----------------------------
# Instantiate Celery with app name, broker, and backend
celery_app = Celery(
    "app_tasks",  # Name of the Celery app
    broker=settings.CELERY_BROKER_URL,  # Broker URL for task queue
    backend=settings.CELERY_RESULT_BACKEND,  # Backend URL for task results
)

# ---------------------------- Auto-Discovery of Tasks ----------------------------
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
    worker_pool="asyncio",            # Use asyncio pool for non-blocking tasks
)

# ---------------------------- Log Initialization ----------------------------
# Log successful Celery app initialization
logger.info("Celery app initialized with broker: %s", settings.CELERY_BROKER_URL)

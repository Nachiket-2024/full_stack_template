# ---------------------------- External Imports ----------------------------
# Celery for async task queue
from celery import Celery

# For logging
import logging

# ---------------------------- Internal Imports ----------------------------
# Load Celery broker & backend URLs from settings
from ..core.settings import settings

# ---------------------------- Logger Setup ----------------------------
# Create module-specific logger
logger = logging.getLogger(__name__)

# ---------------------------- Celery App Initialization ----------------------------
# Create Celery instance with broker and backend
celery_app = Celery(
    "app_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Auto-discover task modules in the email_tasks package
celery_app.autodiscover_tasks(["app.celery.email_tasks"])

# ---------------------------- Celery Configuration ----------------------------
# Update Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Async pool for non-blocking tasks
    worker_pool="asyncio",
)

# Log successful initialization
logger.info("Celery app initialized with broker: %s", settings.CELERY_BROKER_URL)

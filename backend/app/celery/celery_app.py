# ---------------------------- External Imports ----------------------------
# Celery for async task queue
from celery import Celery

# For logging
import logging

# ---------------------------- Internal Imports ----------------------------
# Load Celery broker & backend URLs from settings
from ..core.settings import settings

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Celery App Initialization ----------------------------
# Create Celery instance with broker and backend
celery_app = Celery(
    "app_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Optional: Load task modules automatically (e.g., email_tasks)
celery_app.autodiscover_tasks(["app.celery.email_tasks"])

# ---------------------------- Celery Configuration ----------------------------
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

logger.info("Celery app initialized with broker: %s", settings.CELERY_BROKER_URL)

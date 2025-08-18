# ---------------------------- External Imports ----------------------------
# For async operations and logging
import logging
import traceback

# For sending emails asynchronously
from email.message import EmailMessage
import aiosmtplib

# For Celery task queue
from celery import shared_task

# ---------------------------- Internal Imports ----------------------------
# Load SMTP credentials from settings
from ..core.settings import settings

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Email Sending Task ----------------------------
@shared_task
def send_email_task(to_email: str, subject: str, body: str) -> bool:
    """
    Celery task to send an email asynchronously.
    Uses aiosmtplib to connect to SMTP server.
    """
    try:
        # Compose email
        message = EmailMessage()
        message["From"] = settings.FROM_EMAIL  # e.g., admin email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        # Connect and send using Gmail SMTP asynchronously
        import asyncio

        async def send_async():
            await aiosmtplib.send(
                message,
                hostname="smtp.gmail.com",
                port=587,
                start_tls=True,
                username=settings.FROM_EMAIL,
                password=settings.FROM_EMAIL_PASSWORD
            )

        asyncio.run(send_async())

        logger.info("Email sent to %s", to_email)
        return True

    except Exception:
        logger.error("Error sending email to %s:\n%s", to_email, traceback.format_exc())
        return False

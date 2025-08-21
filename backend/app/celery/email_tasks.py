# ---------------------------- External Imports ----------------------------
# Async email sending and OAuth2 credentials
import aiosmtplib
from email.message import EmailMessage
import logging
import traceback
import asyncio
from google.oauth2.credentials import Credentials

# For Celery task queue
from celery import shared_task

# ---------------------------- Internal Imports ----------------------------
from ..core.settings import settings

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)

# ---------------------------- Async Email Sending Task ----------------------------
@shared_task(bind=True, name="send_email_task")
async def send_email_task(self, to_email: str, subject: str, body: str) -> bool:
    """
    Fully async Celery task to send an email using Gmail OAuth2.
    Refresh token is used to obtain a valid access token dynamically.
    """

    try:
        # ---------------------------- Compose Email ----------------------------
        message = EmailMessage()
        message["From"] = settings.FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        # ---------------------------- Prepare OAuth2 Credentials ----------------------------
        creds = Credentials(
            token=None,
            refresh_token=settings.GOOGLE_EMAIL_REFRESH_TOKEN,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )

        # Refresh token to get access token (run blocking refresh in a thread)
        await asyncio.to_thread(creds.refresh, None)
        access_token = creds.token

        # ---------------------------- Send Email ----------------------------
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=settings.FROM_EMAIL,
            password=access_token,  # OAuth2 access token
        )

        logger.info("Email sent to %s", to_email)
        return True

    except Exception:
        logger.error("Error sending email to %s:\n%s", to_email, traceback.format_exc())
        return False

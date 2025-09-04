# ---------------------------- External Imports ----------------------------
# Async email sending library
import aiosmtplib

# Email message class for constructing emails
from email.message import EmailMessage

# Logging module for tracking events and errors
import logging

# Module to capture full stack traces for debugging exceptions
import traceback

# Asyncio for concurrent async operations
import asyncio

# OAuth2 credentials handling for Google APIs
from google.oauth2.credentials import Credentials

# Celery task queue for background jobs
from celery import shared_task

# ---------------------------- Internal Imports ----------------------------
# Load settings like email credentials and OAuth tokens
from ..core.settings import settings

# ---------------------------- Logger Setup ----------------------------
# Initialize logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Async Email Sending Task ----------------------------
# Celery task to send emails asynchronously
@shared_task(bind=True, name="send_email_task")
async def send_email_task(self, to_email: str, subject: str, body: str) -> bool:

    try:
        # ---------------------------- Compose Email ----------------------------
        # Create a new email message
        message = EmailMessage()
        # Set sender email
        message["From"] = settings.FROM_EMAIL
        # Set recipient email
        message["To"] = to_email
        # Set email subject
        message["Subject"] = subject
        # Set email body/content
        message.set_content(body)

        # ---------------------------- Prepare OAuth2 Credentials ----------------------------
        # Create credentials object with refresh token
        creds = Credentials(
            token=None,
            refresh_token=settings.GOOGLE_EMAIL_REFRESH_TOKEN,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )

        # Refresh token to get access token (blocking operation run in a separate thread)
        await asyncio.to_thread(creds.refresh, None)
        # Extract access token after refresh
        access_token = creds.token

        # ---------------------------- Send Email ----------------------------
        # Send email via Gmail SMTP using OAuth2 token
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=settings.FROM_EMAIL,
            password=access_token,  # OAuth2 access token
        )

        # Log success
        logger.info("Email sent to %s", to_email)
        # Return success
        return True

    except Exception:
        # Log any exception with full stack trace
        logger.error("Error sending email to %s:\n%s", to_email, traceback.format_exc())
        # Return failure
        return False

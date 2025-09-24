# ---------------------------- External Imports ----------------------------
# Async email sending library
import aiosmtplib

# Email message class for constructing emails
from email.message import EmailMessage

# Capture full stack traces for debugging exceptions
import traceback

# Asyncio for running blocking operations asynchronously
import asyncio

# OAuth2 credentials handling for Google APIs
from google.oauth2.credentials import Credentials

# Celery task queue for background jobs
from celery import shared_task

# ---------------------------- Internal Imports ----------------------------
# Load settings like email credentials and OAuth tokens
from ..core.settings import settings

# Import centralized logger factory to create structured, module-specific loggers
from ..logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Async Email Sending Task ----------------------------
@shared_task(bind=True, name="send_email_task")
async def send_email_task(self, to_email: str, subject: str, body: str) -> bool:
    """
    Input:
        1. to_email (str): Recipient email address.
        2. subject (str): Email subject line.
        3. body (str): Email content/body.

    Process:
        1. Compose email using EmailMessage class.
        2. Prepare OAuth2 credentials with refresh token.
        3. Extract access token for SMTP authentication.
        4. Send email via Gmail SMTP using aiosmtplib.
        5. Return true if email sent successfully

    Output:
        1. bool: True if email sent successfully, False otherwise.
    """
    try:
        # Step 1: Compose email using EmailMessage class
        message = EmailMessage()
        message["From"] = settings.FROM_EMAIL    # Sender email
        message["To"] = to_email                 # Recipient email
        message["Subject"] = subject             # Email subject
        message.set_content(body)                # Email body/content

        # Step 2: Prepare OAuth2 credentials with refresh token
        creds = Credentials(
            token=None,
            refresh_token=settings.GOOGLE_EMAIL_REFRESH_TOKEN,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )

        # Refresh token in a separate thread to avoid blocking event loop
        await asyncio.to_thread(creds.refresh, None)

        # Step 3: Extract access token for SMTP authentication
        access_token = creds.token

        # Step 4: Send email via Gmail SMTP using aiosmtplib
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=settings.FROM_EMAIL,
            password=access_token
        )

        # Log successful email delivery
        logger.info("Email sent to %s", to_email)

        # Step 5: Return true if email sent successfully
        return True

    except Exception:
        # Log full exception stack trace
        logger.error("Error sending email to %s:\n%s", to_email, traceback.format_exc())
        return False

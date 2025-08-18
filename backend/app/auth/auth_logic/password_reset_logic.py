# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Auth service CRUDs
from ..auth_services.auth_service import auth_service

# Password service to create and verify reset tokens
from ..auth_services.password_service import password_service

# Celery async email task
from ...celery.email_tasks import send_email_task

# Rate limiter service to prevent abuse
from ..auth_security.rate_limiter_service import rate_limiter_service

# ---------------------------- Logger Setup ----------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Password Reset Request Logic ----------------------------
async def handle_password_reset_request(email: str, ip_address: str):
    """
    Handle password reset request with rate limiting.
    Sends reset token via email if user exists.

    Parameters:
    - email: User email requesting password reset
    - ip_address: Client IP for rate limiting

    Returns:
    - dict: Response message
    - int: HTTP status code
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        email_rate_key = f"pwreset:email:{email}"
        ip_rate_key = f"pwreset:ip:{ip_address}"
        if not await rate_limiter_service.record_request(email_rate_key) or not await rate_limiter_service.record_request(ip_rate_key):
            return {"error": "Too many password reset attempts. Try later."}, 429

        # ---------------------------- Find User and Send Token ----------------------------
        user_found = False
        for role_crud, table_name in [
            (auth_service.role2_crud, "role2"),
            (auth_service.role1_crud, "role1"),
            (auth_service.admin_crud, "admin"),
        ]:
            user = await role_crud.get_by_email(email)
            if user:
                user_found = True
                reset_token = await password_service.create_reset_token(email, table_name)

                # Send token via Celery async email task
                send_email_task.delay(
                    to_email=email,
                    subject="Password Reset",
                    body=f"Your password reset token: {reset_token}"
                )
                break

        # Do not reveal if user exists
        if not user_found:
            logger.info("Password reset requested for non-existing email: %s", email)

        return {"message": "If the email exists, a reset link has been sent."}, 200

    except Exception:
        logger.error("Error during password reset request logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500


# ---------------------------- Password Reset Confirm Logic ----------------------------
async def handle_password_reset_confirm(token: str, new_password: str, ip_address: str):
    """
    Confirm password reset using token, with rate limiting.
    Updates user's hashed password in the database.

    Parameters:
    - token: Password reset token
    - new_password: The new password to set
    - ip_address: Client IP for rate limiting

    Returns:
    - dict: Response message
    - int: HTTP status code
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        # Optional: rate limit per token or IP
        ip_rate_key = f"pwresetconfirm:ip:{ip_address}"
        if not await rate_limiter_service.record_request(ip_rate_key):
            return {"error": "Too many password reset attempts. Try later."}, 429

        # ---------------------------- Verify Token ----------------------------
        payload_data = await password_service.verify_reset_token(token)
        if not payload_data:
            return {"error": "Invalid or expired token"}, 400

        email = payload_data["sub"]
        table_name = payload_data["table"]

        # ---------------------------- Update Password ----------------------------
        crud_instance = {
            "admin": auth_service.admin_crud,
            "role1": auth_service.role1_crud,
            "role2": auth_service.role2_crud,
        }.get(table_name)

        if not crud_instance:
            return {"error": "Invalid token data"}, 400

        hashed_password = await password_service.hash_password(new_password)
        await crud_instance.update_by_email(email, {"hashed_password": hashed_password})

        return {"message": "Password has been reset successfully"}, 200

    except Exception:
        logger.error("Error during password reset confirm logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500

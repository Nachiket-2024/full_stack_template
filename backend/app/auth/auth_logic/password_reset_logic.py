# ---------------------------- External Imports ----------------------------
# For logging and handling exceptions
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import the core password reset service
from ..auth_services.password_reset_service import password_reset_service

# Rate limiter service to prevent abuse
from ..auth_security.rate_limiter_service import rate_limiter_service

# Role tables to find users
from ...core.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------- Password Reset Request Handler ----------------------------
async def handle_password_reset_request(email: str, ip_address: str):
    """
    Handle password reset request with rate limiting.
    Sends reset token via email if user exists.
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        # Limit requests per email
        email_rate_key = f"pwreset:email:{email}"
        # Limit requests per IP
        ip_rate_key = f"pwreset:ip:{ip_address}"

        # Reject if limits exceeded
        if not await rate_limiter_service.record_request(email_rate_key) or not await rate_limiter_service.record_request(ip_rate_key):
            return {"error": "Too many password reset attempts. Try later."}, 429

        # ---------------------------- Find User and Send Token ----------------------------
        user_found = False
        for role, crud in ROLE_TABLES.items():
            user = await crud.get_by_email(email)
            if user:
                user_found = True
                # Use core service to send reset email
                await password_reset_service.send_reset_email(email, role)
                break

        # Log request for non-existing emails without revealing info
        if not user_found:
            logger.info("Password reset requested for non-existing email: %s", email)

        # Generic success response
        return {"message": "If the email exists, a reset link has been sent."}, 200

    except Exception:
        # Log unexpected errors
        logger.error("Error during password reset request logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500

# ---------------------------- Password Reset Confirm Handler ----------------------------
async def handle_password_reset_confirm(token: str, new_password: str, ip_address: str):
    """
    Confirm password reset using token, with rate limiting.
    Updates user's hashed password in the database.
    """
    try:
        # ---------------------------- Rate Limiting ----------------------------
        ip_rate_key = f"pwresetconfirm:ip:{ip_address}"
        if not await rate_limiter_service.record_request(ip_rate_key):
            return {"error": "Too many password reset attempts. Try later."}, 429

        # ---------------------------- Reset Password ----------------------------
        # Call core service to reset password
        success = await password_reset_service.reset_password(token, new_password)
        if not success:
            return {"error": "Invalid token or password"}, 400

        # Success response
        return {"message": "Password has been reset successfully"}, 200

    except Exception:
        # Log unexpected errors
        logger.error("Error during password reset confirm logic:\n%s", traceback.format_exc())
        return {"error": "Internal Server Error"}, 500

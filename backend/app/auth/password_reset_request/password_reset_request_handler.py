# ---------------------------- External Imports ----------------------------
# Logging module for tracking events, warnings, and debugging
import logging

# Module to capture detailed exception stack traces
import traceback

# FastAPI class for sending JSON responses to clients
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Core password reset service for sending reset tokens via email
from ..password_logic.password_reset_service import password_reset_service

# Role tables for finding users across different roles in the system
from ...access_control.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Initialize a logger specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Password Reset Request Handler Class ----------------------------
# Class responsible for handling password reset request flow
class PasswordResetRequestHandler:
    """
    1. handle_password_reset_request - Process password reset requests and send reset token if user exists.
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with required services and role tables
    def __init__(self):
        # Assign password reset service to instance
        self.password_reset_service = password_reset_service
        # Assign role tables for user lookup to instance
        self.role_tables = ROLE_TABLES

    # ---------------------------- Handle Password Reset Request ----------------------------
    # Async method to process password reset request and send token if user exists
    async def handle_password_reset_request(self, email: str):
        """
        Input:
            1. email (str): Email address of the user requesting password reset.

        Process:
            1. Check each role table to find if a user exists with the given email.
            2. If user exists, send password reset email via password_reset_service.
            3. Log requests for non-existing emails without revealing sensitive info.
            4. Return generic response to prevent email enumeration.

        Output:
            1. JSONResponse: Message indicating reset link sent or internal server error on failure.
        """
        try:
            # ---------------------------- Initialize User Found Flag ----------------------------
            # Flag to track if a user exists for the given email
            user_found = False

            # ---------------------------- Search Across Roles ----------------------------
            # Iterate over all role tables to find the user by email
            for role, crud in self.role_tables.items():
                user = await crud.get_by_email(email)  # Query user in current role table

                # ---------------------------- Send Reset Email if User Exists ----------------------------
                # If user exists, send reset email and stop further searching
                if user:
                    user_found = True
                    await self.password_reset_service.send_reset_email(email, role)
                    break  # Stop loop once user is found

            # ---------------------------- Log Non-existing Email Requests ----------------------------
            # Log request for non-existing emails without revealing sensitive info
            if not user_found:
                logger.info("Password reset requested for non-existing email: %s", email)

            # ---------------------------- Return Generic Success Response ----------------------------
            # Return a generic success response to prevent email enumeration
            return JSONResponse(
                content={"message": "If the email exists, a reset link has been sent."},
                status_code=200
            )

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log any exceptions with full stack trace
            logger.error("Error during password reset request logic:\n%s", traceback.format_exc())
            # Return generic internal server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Instantiate PasswordResetRequestHandler ----------------------------
# Singleton instance of the handler for route usage
password_reset_request_handler = PasswordResetRequestHandler()

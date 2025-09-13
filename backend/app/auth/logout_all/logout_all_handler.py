# ---------------------------- External Imports ----------------------------
# Logging modules for tracking events and debugging errors
import logging
import traceback

# FastAPI response class for sending JSON responses to clients
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# JWT service for handling token revocation and validation
from ..token_logic.jwt_service import jwt_service

# ---------------------------- Logger Setup ----------------------------
# Logger instance for capturing errors and debug information
logger = logging.getLogger(__name__)

# ---------------------------- Logout All Handler Class ----------------------------
# Handler class for logging a user out from all devices
class LogoutAllHandler:
    """
    1. handle_logout_all - Revoke all refresh tokens for the user and clear authentication cookies.
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize LogoutAllHandler with required services
    def __init__(self):
        self.jwt_service = jwt_service

    # ---------------------------- Logout All Method ----------------------------
    # Async method to revoke all tokens for a user
    async def handle_logout_all(self, refresh_token: str | None, db):
        """
        Input:
            1. refresh_token (str | None): Refresh token from user's cookie.
            2. db: Database session for token revocation operations.

        Process:
            1. Validate that refresh token is provided.
            2. Revoke all refresh tokens for the user using JWT service.
            3. Check number of tokens revoked and handle error if none.
            4. Clear access and refresh cookies.
            5. Return appropriate JSONResponse.

        Output:
            1. JSONResponse: Success message with count of devices logged out or error message.
        """
        try:
            # Return error if no refresh token is provided
            if not refresh_token:
                return JSONResponse(
                    content={"error": "No refresh token cookie found"},
                    status_code=400
                )

            # Revoke all refresh tokens associated with this user
            revoked_count = await self.jwt_service.revoke_all_refresh_tokens_for_user(refresh_token, db=db)

            # Return error if no tokens were revoked
            if revoked_count == 0:
                return JSONResponse(
                    content={"error": "Invalid refresh token or no tokens to revoke"},
                    status_code=400
                )

            # Prepare response and delete access and refresh cookies
            resp = JSONResponse(
                content={"message": f"Logged out from {revoked_count} devices"},
                status_code=200
            )
            resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")
            resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")

            # Return the prepared response
            return resp

        # Catch all unexpected errors
        except Exception:
            # Log full traceback for debugging
            logger.error("Error during logout-all logic:\n%s", traceback.format_exc())
            
            # Return generic internal server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Instantiate LogoutAllHandler ----------------------------
# Singleton instance for use in routes
logout_all_handler = LogoutAllHandler()

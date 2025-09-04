# ---------------------------- External Imports ----------------------------
# Logging for tracking events and debugging
import logging
import traceback

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to revoke tokens
from ..refresh_token_logic.refresh_token_service import refresh_token_service

# ---------------------------- Logger Setup ----------------------------
# Configure module-specific logger
logger = logging.getLogger(__name__)

# ---------------------------- Logout Handler Class ----------------------------
# Handler class for managing user logout operations
class LogoutHandler:
    """
    1. handle_logout - Revoke refresh token, clear cookies, and return logout response.
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize LogoutHandler with required services
    def __init__(self):
        self.refresh_token_service = refresh_token_service

    # ---------------------------- Logout Method ----------------------------
    # Async method to handle user logout
    async def handle_logout(self, refresh_token: str | None):
        """
        Input:
            1. refresh_token (str | None): Refresh token from user's cookie.

        Process:
            1. Validate that refresh token is provided.
            2. Revoke the refresh token using refresh_token_service.
            3. Clear access and refresh cookies if revocation succeeds.
            4. Return appropriate JSONResponse.

        Output:
            1. JSONResponse: Success message if logout succeeds or error details otherwise.
        """
        try:
            # ---------------------------- Validate Token ----------------------------
            # Return error if no refresh token is provided
            if not refresh_token:
                return JSONResponse(
                    content={"error": "No refresh token cookie found"},
                    status_code=400
                )

            # ---------------------------- Revoke Token ----------------------------
            # Attempt to revoke the refresh token
            success = await self.refresh_token_service.revoke_refresh_token(refresh_token)

            # ---------------------------- Check Revocation Result ----------------------------
            # Return error if revocation failed
            if not success:
                return JSONResponse(
                    content={"error": "Invalid refresh token or already revoked"},
                    status_code=400
                )

            # ---------------------------- Clear Cookies ----------------------------
            # Create response and delete access and refresh cookies
            resp = JSONResponse(
                content={"message": "Logged out successfully"},
                status_code=200
            )
            resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")
            resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")

            # Return the response
            return resp

        # ---------------------------- Exception Handling ----------------------------
        # Catch all unexpected errors
        except Exception:
            # Log full traceback for debugging
            logger.error("Error during logout logic:\n%s", traceback.format_exc())
            # Return generic internal server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Instantiate LogoutHandler ----------------------------
# Singleton instance for route usage
logout_handler = LogoutHandler()

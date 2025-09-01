# ---------------------------- External Imports ----------------------------
# Logging for tracking events and debugging
import logging
import traceback

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to revoke tokens
from ..token_logic.refresh_token_service import refresh_token_service

# ---------------------------- Logger Setup ----------------------------
# Configure module-specific logger
logger = logging.getLogger(__name__)

# ---------------------------- Logout Handler Class ----------------------------
# Class responsible for handling user logout flow
class LogoutHandler:
    """
    Handles user logout:
    - Reads refresh token from cookies
    - Revokes refresh tokens via refresh_token_service
    - Clears access and refresh token cookies
    - Returns JSONResponse with appropriate status
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize handler with required services
    def __init__(self):
        self.refresh_token_service = refresh_token_service

    # ---------------------------- Logout Method ----------------------------
    # Process logout request and revoke refresh token
    async def handle_logout(self, refresh_token: str | None):
        """
        Process logout request and return JSONResponse.

        Parameters:
        - refresh_token: The user's refresh token from cookie

        Returns:
        - JSONResponse with success or error message
        """
        try:
            # ---------------------------- Validate Token ----------------------------
            # If no refresh token is provided in cookies, return error response
            if not refresh_token:
                return JSONResponse(
                    content={"error": "No refresh token cookie found"},
                    status_code=400
                )

            # ---------------------------- Revoke Token ----------------------------
            # Attempt to revoke the refresh token
            success = await self.refresh_token_service.revoke_refresh_token(refresh_token)

            # ---------------------------- Check Revocation Result ----------------------------
            # If revocation failed, return error response
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

        except Exception:
            # Log full traceback for debugging
            logger.error("Error during logout logic:\n%s", traceback.format_exc())
            # Return generic server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

# ---------------------------- Instantiate LogoutHandler ----------------------------
# Singleton instance for route usage
logout_handler = LogoutHandler()

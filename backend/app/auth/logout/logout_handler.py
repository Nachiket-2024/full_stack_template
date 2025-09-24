# ---------------------------- External Imports ----------------------------
# Capture full stack traces in case of exceptions
import traceback

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to handle revocation and management
from ..refresh_token_logic.refresh_token_service import refresh_token_service

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Logout Handler Class ----------------------------
# Handler class for managing user logout operations
class LogoutHandler:
    """
    1. handle_logout - Revoke refresh token, clear cookies, and return logout response.
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize with a reference to the refresh token service
    def __init__(self):
        # Step 1: Store reference to refresh token service for reuse
        self.refresh_token_service = refresh_token_service

    # ---------------------------- Handle Logout ----------------------------
    # Async method to revoke refresh token and clear authentication cookies
    async def handle_logout(self, refresh_token: str | None) -> JSONResponse:
        """
        Input:
            1. refresh_token (str | None): Refresh token from user's cookie.

        Process:
            1. Validate that refresh token is provided.
            2. Return error if refresh token is missing.
            3. Revoke the refresh token using refresh_token_service.
            4. Handle failure if token revocation was unsuccessful.
            5. Prepare JSONResponse for successful logout.
            6. Delete access token cookie.
            7. Delete refresh token cookie.
            8. Return final response.

        Output:
            1. JSONResponse: Success message if logout succeeds or error details otherwise.
        """
        try:
            # Step 1: Validate that refresh token is provided
            if not refresh_token:
                # Step 2: Return error if refresh token is missing
                return JSONResponse(
                    content={"error": "No refresh token cookie found"},
                    status_code=400
                )

            # Step 3: Revoke the refresh token using refresh_token_service
            success = await self.refresh_token_service.revoke_refresh_token(refresh_token)

            # Step 4: Handle failure if token revocation was unsuccessful
            if not success:
                return JSONResponse(
                    content={"error": "Invalid refresh token or already revoked"},
                    status_code=400
                )

            # Step 5: Prepare JSONResponse for successful logout
            resp = JSONResponse(
                content={"message": "Logged out successfully"},
                status_code=200
            )

            # Step 6: Delete access token cookie
            resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")

            # Step 7: Delete refresh token cookie
            resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")

            # Step 8: Return final response
            return resp

        except Exception:
            # Handle unexpected exceptions and log errors
            logger.error("Error during logout logic:\n%s", traceback.format_exc())

            # Return internal server error response on exception
            return JSONResponse(
                content={"error": "Internal Server Error"},
                status_code=500
            )


# ---------------------------- Singleton Instance ----------------------------
# Singleton instance of LogoutHandler for route usage
logout_handler = LogoutHandler()

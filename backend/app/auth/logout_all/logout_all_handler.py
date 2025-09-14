# ---------------------------- External Imports ----------------------------
# Import logging module for capturing events and errors
import logging

# Import traceback for detailed error stack traces
import traceback

# Import JSONResponse for returning structured JSON responses in FastAPI
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Import refresh token service for DB + Redis revocations
from ..refresh_token_logic.refresh_token_service import refresh_token_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- Logout All Handler Class ----------------------------
# Handler class for logging a user out from all devices
class LogoutAllHandler:
    """
    1. handle_logout_all - Revoke all refresh tokens for the user and clear authentication cookies.
    """

    # ---------------------------- Logout All Method ----------------------------
    # Async method to revoke all tokens for a user
    async def handle_logout_all(self, refresh_token: str | None, db):
        """
        Input:
            1. refresh_token (str | None): Refresh token from user's cookie.
            2. db: Database session for token revocation operations.

        Process:
            1. Validate that refresh token is provided.
            2. Revoke all refresh tokens for the user using RefreshTokenService.
            3. Check number of tokens revoked and handle error if none.
            4. Clear access and refresh cookies.
            5. Return appropriate JSONResponse.

        Output:
            1. JSONResponse: Success message with count of devices logged out or error message.
        """
        try:
            # If refresh token is missing, return 400 Bad Request
            if not refresh_token:
                # Return JSON error response
                return JSONResponse(
                    content={"error": "No refresh token cookie found"},
                    status_code=400
                )

            # Call refresh_token_service to revoke all tokens for this user
            revoked_count = await refresh_token_service.revoke_all_tokens_for_email(
                refresh_token, db=db
            )

            # If no tokens were revoked, return error response
            if revoked_count == 0:
                # Return JSON error response
                return JSONResponse(
                    content={"error": "Invalid refresh token or no tokens to revoke"},
                    status_code=400
                )

            # Create success JSON response
            resp = JSONResponse(
                content={"message": f"Logged out from {revoked_count} devices"},
                status_code=200
            )

            # Delete access token cookie
            resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")

            # Delete refresh token cookie
            resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")

            # Return success response with cookies cleared
            return resp

        # Handle unexpected errors gracefully
        except Exception:
            # Log error with traceback for debugging
            logger.error("Error during logout-all logic:\n%s", traceback.format_exc())

            # Return generic internal server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Instantiate LogoutAllHandler ----------------------------
# Create singleton instance for reuse in routes
logout_all_handler = LogoutAllHandler()

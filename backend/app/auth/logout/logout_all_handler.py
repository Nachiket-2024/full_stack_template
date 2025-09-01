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
# Class that handles logging out a user from all devices
class LogoutAllHandler:
    """
    Handles user logout from all devices:
    - Reads refresh token from cookies
    - Revokes all refresh tokens for the user
    - Clears access and refresh token cookies
    - Returns JSONResponse with status
    """

    # ---------------------------- Constructor ----------------------------
    # Initialize the handler with required services
    def __init__(self):
        # Assign JWT service for token operations
        self.jwt_service = jwt_service

    # ---------------------------- Logout All Method ----------------------------
    # Method to revoke all refresh tokens for a user and clear cookies
    async def handle_logout_all(self, refresh_token: str | None, db):
        """
        Revoke all refresh tokens for a user and return JSONResponse.

        Parameters:
        - refresh_token: Refresh token from cookie
        - db: AsyncSession for database operations

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

            # ---------------------------- Revoke All Tokens ----------------------------
            # Use JWT service to revoke all refresh tokens associated with this user
            revoked_count = await self.jwt_service.revoke_all_refresh_tokens_for_user(refresh_token, db=db)

            # ---------------------------- Check Revocation Result ----------------------------
            # If no tokens were revoked, respond with an error
            if revoked_count == 0:
                return JSONResponse(
                    content={"error": "Invalid refresh token or no tokens to revoke"},
                    status_code=400
                )

            # ---------------------------- Clear Cookies ----------------------------
            # Prepare response and delete both access and refresh cookies
            resp = JSONResponse(
                content={"message": f"Logged out from {revoked_count} devices"},
                status_code=200
            )
            resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")
            resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")

            # Return the prepared response
            return resp

        except Exception:
            # Log full traceback to help with debugging
            logger.error("Error during logout-all logic:\n%s", traceback.format_exc())
            # Return generic internal server error response
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

# ---------------------------- Instantiate LogoutAllHandler ----------------------------
# Create a singleton instance for use in routes
logout_all_handler = LogoutAllHandler()

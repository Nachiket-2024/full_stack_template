# ---------------------------- External Imports ----------------------------
# Logging for structured event and error logging
import logging

# Capture full stack traces in case of exceptions
import traceback

# FastAPI response class for sending JSON responses
from fastapi.responses import JSONResponse

# ---------------------------- Internal Imports ----------------------------
# Refresh token service to handle revocation of tokens
from ..refresh_token_logic.refresh_token_service import refresh_token_service

# JWT service for verifying tokens
from ..token_logic.jwt_service import jwt_service

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance specific to this module
logger = logging.getLogger(__name__)

# ---------------------------- Logout All Handler Class ----------------------------
# Handler class for revoking all refresh tokens and clearing authentication cookies
class LogoutAllHandler:
    """
    1. handle_logout_all - Revoke all refresh tokens for the user and clear authentication cookies.
    """

    # ---------------------------- Initialization ----------------------------
    # Constructor method (no initialization logic required)
    def __init__(self):
        # No initialization logic required
        pass

    # ---------------------------- Handle Logout All ----------------------------
    # Async method to revoke all tokens and clear cookies
    async def handle_logout_all(self, refresh_token: str | None) -> JSONResponse:
        """
        Input:
            1. refresh_token (str | None): Refresh token from user's cookie.

        Process:
            1. Validate that refresh token is provided.
            2. Verify refresh token and extract user ID.
            3. Revoke all refresh tokens for the user.
            4. Return error if no tokens were revoked.
            5. Clear authentication cookies on successful logout.
            6. Prepare JSON response with number of devices logged out.
            7. Return final response.

        Output:
            1. JSONResponse: Success or error message.
        """
        try:
            # Step 1: Validate that refresh token is provided
            if not refresh_token:
                return JSONResponse(
                    content={"error": "No refresh token cookie found"},
                    status_code=400
                )

            # Step 2: Verify refresh token and extract user ID
            payload = await jwt_service.verify_token(refresh_token)

            # Step 3: Return error if refresh token is invalid
            if not payload or "sub" not in payload:
                return JSONResponse(
                    content={"error": "Invalid refresh token"},
                    status_code=400
                )

            # Step 4: Extract user ID from token payload
            user_id = payload["sub"]

            # Step 5: Revoke all refresh tokens for the user
            revoked_count = await refresh_token_service.revoke_all_tokens_for_user(user_id)

            # Step 6: Return error if no tokens were revoked
            if revoked_count == 0:
                return JSONResponse(
                    content={"error": "No tokens to revoke"},
                    status_code=400
                )

            # Step 7: Clear authentication cookies and prepare response
            resp = JSONResponse(
                content={"message": f"Logged out from {revoked_count} devices"},
                status_code=200
            )
            resp.delete_cookie(key="access_token", httponly=True, secure=True, samesite="Strict")
            resp.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="Strict")

            # Step 8: Return final response
            return resp

        except Exception:
            # Handle unexpected exceptions and log errors
            logger.error("Error during logout-all logic:\n%s", traceback.format_exc())

            # Return error response on exception
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------------- Instantiate Logout All Handler ----------------------------
# Singleton instance for use in routes
logout_all_handler = LogoutAllHandler()

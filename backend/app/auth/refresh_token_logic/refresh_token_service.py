# ---------------------------- External Imports ----------------------------
# Capture full stack traces in case of exceptions
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import JWT service for token creation, verification, and revocation
from ..token_logic.jwt_service import jwt_service

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Refresh Token Service Class ----------------------------
# Service class responsible for refresh token operations using Redis only
class RefreshTokenService:
    """
    1. refresh_tokens - Rotate refresh token and generate new access token.
    2. revoke_refresh_token - Revoke a single refresh token in Redis.
    3. revoke_all_tokens_for_user - Revoke all refresh tokens for a user in Redis.
    """

    # ---------------------------- Refresh Tokens ----------------------------
    @staticmethod
    async def refresh_tokens(refresh_token: str) -> dict[str, str] | None:
        """
        Input:
            refresh_token (str): The refresh token provided by the client.

        Process:
            1. Check if the refresh token is revoked.
            2. Verify the refresh token and extract payload.
            3. Extract email and role from payload.
            4. Revoke the old refresh token in Redis.
            5. Generate a new access token.
            6. Generate a new refresh token.
            7. Return dictionary with both new tokens if successful.

        Output:
            dict[str, str] containing "access_token" and "refresh_token", or None if invalid.
        """
        try:
            # Step 1: Check if the refresh token is revoked
            if await jwt_service.is_token_revoked(refresh_token):
                logger.warning("Attempt to use revoked refresh token")
                return None

            # Step 2: Verify the refresh token and extract payload
            payload = await jwt_service.verify_token(refresh_token)

            if not payload:
                return None

            # Step 3: Extract email and role from payload
            email = payload.get("email")
            role = payload.get("role")

            if not email or not role:
                return None

            # Step 4: Revoke the old refresh token in Redis
            await jwt_service.revoke_token(refresh_token, email)

            # Step 5: Generate a new access token
            new_access_token = await jwt_service.create_access_token(email, role)

            # Step 6: Generate a new refresh token
            new_refresh_token = await jwt_service.create_refresh_token(email, role)

            # Step 7: Return dictionary with both new tokens if successful
            return {"access_token": new_access_token, "refresh_token": new_refresh_token}

        except Exception:
            logger.error("Error refreshing token:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        """
        Input:
            refresh_token (str): The refresh token to revoke.

        Process:
            1. Verify the refresh token and extract payload.
            2. Extract email from payload.
            3. Revoke the refresh token in Redis.
            4. Return True if revocation succeeds.

        Output:
            bool: True if successfully revoked, False otherwise.
        """
        try:
            # Step 1: Verify the refresh token and extract payload
            payload = await jwt_service.verify_token(refresh_token)

            if not payload:
                return False

            # Step 2: Extract email from payload
            email = payload.get("email")

            if not email:
                return False

            # Step 3: Revoke the refresh token in Redis
            await jwt_service.revoke_token(refresh_token, email)

            # Step 4: Return True if revocation succeeds
            return True

        except Exception:
            logger.error("Error revoking refresh token:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Revoke All Tokens for User ----------------------------
    @staticmethod
    async def revoke_all_tokens_for_user(email: str) -> int:
        """
        Input:
            email (str): The email of the user whose tokens should be revoked.

        Process:
            1. Fetch all refresh tokens for the user from Redis.
            2. Revoke each refresh token.
            3. Return the count of successfully revoked tokens.

        Output:
            int: Number of tokens revoked for the user.
        """
        try:
            # Step 1: Fetch all refresh tokens for the user from Redis
            tokens = await jwt_service.get_all_refresh_tokens_for_user(email)

            if not tokens:
                return 0

            revoked_count = 0

            # Step 2: Revoke each refresh token
            for token in tokens:
                if await jwt_service.revoke_token(token, email):
                    revoked_count += 1

            # Step 3: Return the count of successfully revoked tokens
            return revoked_count

        except Exception:
            logger.error("Error revoking all tokens for user %s:\n%s", email, traceback.format_exc())
            return 0


# ---------------------------- Singleton Instance ----------------------------
# Create single global instance of RefreshTokenService for application usage
refresh_token_service = RefreshTokenService()

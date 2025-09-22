# ---------------------------- External Imports ----------------------------
# Import logging module for async logging and tracing
import logging

# Import traceback module to capture full stack traces
import traceback

# ---------------------------- Internal Imports ----------------------------
# Import JWT service for token creation, verification, and revocation
from ..token_logic.jwt_service import jwt_service

# ---------------------------- Logger Setup ----------------------------
# Create logger instance specific to this module
logger = logging.getLogger(__name__)

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
            1. refresh_token (str): Existing refresh token to be rotated.

        Process:
            1. Check if refresh token is already revoked in Redis.
            2. Verify refresh token payload and extract user info.
            3. Revoke old refresh token in Redis.
            4. Generate new access and refresh tokens and store new refresh token in Redis.

        Output:
            1. dict: Contains new access_token and refresh_token or None on failure.
        """
        try:
            # -------1. Check if refresh token is already revoked in Redis-------
            if await jwt_service.is_token_revoked(refresh_token):
                logger.warning("Attempt to use revoked refresh token")
                return None

            # -------2. Verify refresh token payload and extract user info--------
            payload = await jwt_service.verify_token(refresh_token)

            if not payload:
                logger.warning("Invalid or expired refresh token")
                return None

            user_id = payload.get("user_id")
            device_id = payload.get("device_id")

            if not user_id or not device_id:
                logger.warning("Malformed refresh token payload")
                return None

            # -----------------3. Revoke old refresh token in Redis-----------------
            await jwt_service.revoke_refresh_token(refresh_token)

            # --------4. Generate new access and refresh tokens and store---------
            new_access_token = await jwt_service.create_access_token(user_id, device_id)
            new_refresh_token = await jwt_service.create_refresh_token(user_id, device_id)

            return {"access_token": new_access_token, "refresh_token": new_refresh_token}

        except Exception:
            logger.error("Unexpected error in refreshing tokens:\n%s", traceback.format_exc())
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        """
        Input:
            1. refresh_token (str): Refresh token to revoke.

        Process:
            1. Verify token payload to extract user info.
            2. Revoke token in Redis.

        Output:
            1. bool: True if successfully revoked, False otherwise.
        """
        try:
            # -------1. Verify token payload to extract user info-------
            payload = await jwt_service.verify_token(refresh_token)
            
            if not payload:
                return False

            user_id = payload.get("user_id")
            device_id = payload.get("device_id")

            if not user_id or not device_id:
                return False

            # -----------------2. Revoke token in Redis-----------------
            return await jwt_service.revoke_refresh_token(refresh_token)

        except Exception:
            logger.error("Unexpected error in revoking refresh token:\n%s", traceback.format_exc())
            return False

    # ---------------------------- Revoke All Tokens for User ----------------------------
    @staticmethod
    async def revoke_all_tokens_for_user(user_id: str) -> int:
        """
        Input:
            1. user_id (str): User identifier to revoke all tokens for.

        Process:
            1. Fetch all active refresh tokens for the user from Redis.
            2. Revoke all tokens in Redis.

        Output:
            1. int: Number of tokens successfully revoked.
        """
        try:
            # -------1. Fetch all active refresh tokens for the user from Redis-------
            all_tokens = await jwt_service.get_all_refresh_tokens_for_user(user_id)
            if not all_tokens:
                return 0

            # -----------------2. Revoke all tokens in Redis-----------------
            return await jwt_service.revoke_all_refresh_tokens_for_user(all_tokens)

        except Exception:
            logger.error(
                "Error revoking all tokens for user %s:\n%s",
                user_id,
                traceback.format_exc(),
            )
            return 0


# ---------------------------- Service Instance ----------------------------
# Singleton instance of RefreshTokenService for importing elsewhere
refresh_token_service = RefreshTokenService()

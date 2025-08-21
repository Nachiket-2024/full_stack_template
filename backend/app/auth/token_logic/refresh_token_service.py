# ---------------------------- External Imports ----------------------------
# For async logging and traceback
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Reuse JWT creation, verification, and revocation
from .jwt_service import jwt_service

# Role → DB table mapping to update refresh token
from ...core.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create logger for this module
logger = logging.getLogger(__name__)

# ---------------------------- Refresh Token Service ----------------------------
class RefreshTokenService:
    """
    Service to handle refresh token rotation:
      - Verify old refresh token
      - Revoke old token in Redis
      - Issue new access + refresh tokens
      - Update DB with new refresh token (only one active per user)
    """

    # ---------------------------- Refresh Tokens ----------------------------
    @staticmethod
    async def refresh_tokens(refresh_token: str) -> dict[str, str] | None:
        """
        Refresh flow:
          1. Verify old refresh token
          2. Check revocation list
          3. Revoke old token
          4. Issue new access + refresh tokens
          5. Persist new refresh token in DB
        Returns dict with {"access_token": str, "refresh_token": str}
        or None if invalid/revoked.
        """
        try:
            # Step 1: Check if token already revoked in Redis
            if await jwt_service.is_token_revoked(refresh_token):
                logger.warning("Attempt to use revoked refresh token")
                return None

            # Step 2: Verify the refresh token payload
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                logger.warning("Invalid or expired refresh token")
                return None

            # Extract subject (email) and role
            email, role = payload.get("sub"), payload.get("role")
            if not email or not role:
                logger.warning("Malformed refresh token payload")
                return None

            # Step 3: Revoke the old refresh token
            await jwt_service.revoke_refresh_token(refresh_token)

            # Step 4: Issue new tokens
            new_access_token = await jwt_service.create_access_token(email, role)
            new_refresh_token = await jwt_service.create_refresh_token(email, role)

            # Step 5: Persist the new refresh token in DB
            table = ROLE_TABLES.get(role)
            if not table:
                logger.error(f"No table mapping found for role: {role}")
                return None
            await table.update_refresh_token(email=email, refresh_token=new_refresh_token)

            # Return both new tokens
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }

        # Handle unexpected errors gracefully
        except Exception:
            logger.error(
                "Unexpected error in refreshing tokens:\n%s",
                traceback.format_exc(),
            )
            return None

    # ---------------------------- Revoke Refresh Token ----------------------------
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        """
        Explicitly revoke a refresh token:
          - Decodes expiry
          - Stores revocation marker in Redis until expiry
        Returns True if revoked, False if invalid/expired.
        """
        try:
            # Use JWTService revoke method directly
            return await jwt_service.revoke_refresh_token(refresh_token)

        except Exception:
            logger.error(
                "Unexpected error in revoking refresh token:\n%s",
                traceback.format_exc(),
            )
            return False


# ---------------------------- Service Instance ----------------------------
# Singleton instance to be imported in other modules
refresh_token_service = RefreshTokenService()

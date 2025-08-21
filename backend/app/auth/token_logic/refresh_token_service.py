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

            # Extract email and table
            email, table = payload.get("email"), payload.get("table")
            if not email or not table:
                logger.warning("Malformed refresh token payload")
                return None

            # Step 3: Revoke the old refresh token
            await jwt_service.revoke_refresh_token(refresh_token)

            # Step 4: Issue new tokens
            new_access_token = await jwt_service.create_access_token(email, table)
            new_refresh_token = await jwt_service.create_refresh_token(email, table)

            # Step 5: Persist the new refresh token in DB
            table = ROLE_TABLES.get(table)
            if not table:
                logger.error(f"No table mapping found for table: {table}")
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
        
    # ---------------------------- Revoke All Tokens for Email ----------------------------
    @staticmethod
    async def revoke_all_tokens_for_email(refresh_token: str, db) -> int:
        """
        Revoke all refresh tokens for the user identified by the provided refresh token.
        Uses the table from the token payload instead of looping through all tables.

        Parameters:
        - refresh_token: The refresh token provided by the client
        - db: AsyncSession for database operations

        Returns:
        - Number of tokens revoked (0 if invalid/malformed token)
        """
        try:
            # Verify the refresh token payload
            payload = await jwt_service.verify_token(refresh_token)
            if not payload:
                return 0

            # Extract email and table from payload
            email, table = payload.get("email"), payload.get("table")
            if not email or not table:
                return 0

            # Get the correct table object
            table_obj = ROLE_TABLES.get(table)
            if not table_obj:
                logger.error(f"No table mapping found for table: {table}")
                return 0

            # Revoke all refresh tokens for this user in the table
            revoked_count = await table_obj.revoke_all_refresh_tokens(email, db=db)
            return revoked_count

        except Exception:
            logger.error("Error revoking all tokens for email from token %s:\n%s", refresh_token, traceback.format_exc())
            return 0


# ---------------------------- Service Instance ----------------------------
# Singleton instance to be imported in other modules
refresh_token_service = RefreshTokenService()

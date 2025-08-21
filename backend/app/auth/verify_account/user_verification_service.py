# ---------------------------- External Imports ----------------------------
# For logging and capturing errors
import logging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Role tables for looking up users and updating verification status
from ...core.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- User Verification Service ----------------------------
class UserVerificationService:
    """
    Handles marking user accounts as verified in the database.
    Works with multiple role tables.
    
    Responsibilities:
    1. Check if the user exists in any role table.
    2. Update the 'is_verified' field to True if not already verified.
    3. Return True if successfully updated, False otherwise.
    """

    # ---------------------------- Mark User Verified Method ----------------------------
    @staticmethod
    async def mark_user_verified(email: str) -> bool:
        """
        Marks a user as verified based on their email.
        
        Parameters:
        - email: User's email address to verify
        
        Returns:
        - True if user was found and marked as verified
        - False if user not found or already verified
        """
        try:
            # Loop through all role tables
            for role_name, crud in ROLE_TABLES.items():
                # Look up user by email
                user = await crud.get_by_email(email)
                
                # If user exists and is not already verified
                if user and not getattr(user, "is_verified", False):
                    # Update 'is_verified' field in DB
                    await crud.update_by_email(email, {"is_verified": True})
                    logger.info("User %s marked as verified in table %s", email, role_name)
                    return True

            # User not found or already verified
            return False

        except Exception:
            # Log unexpected errors
            logger.error("Error marking user verified:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
user_verification_service = UserVerificationService()

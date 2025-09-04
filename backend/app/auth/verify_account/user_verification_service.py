# ---------------------------- External Imports ----------------------------
# For logging events, warnings, and errors
import logging

# Capture full exception stack traces for debugging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Role tables for looking up users and updating verification status
from ...access_control.role_tables import ROLE_TABLES

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# ---------------------------- User Verification Service Class ----------------------------
# Service to handle marking users as verified
class UserVerificationService:
    """
    1. mark_user_verified - Mark a user as verified across role tables.
    """

    # ---------------------------- Mark User Verified ----------------------------
    @staticmethod
    async def mark_user_verified(email: str) -> bool:
        """
        Input:
            1. email (str): Email of the user to verify.

        Process:
            1. Iterate over all role tables to locate the user.
            2. Check if user exists and is not already verified.
            3. Update 'is_verified' field to True in the database.

        Output:
            1. bool: True if verification succeeded, False otherwise.
        """
        try:
            # ---------------------------- Iterate Role Tables ----------------------------
            for role_name, crud in ROLE_TABLES.items():
                # ---------------------------- Lookup User by Email ----------------------------
                user = await crud.get_by_email(email)
                
                # ---------------------------- Check Verification Status ----------------------------
                if user and not getattr(user, "is_verified", False):
                    # ---------------------------- Update User Verification ----------------------------
                    await crud.update_by_email(email, {"is_verified": True})

                    # ---------------------------- Log Success ----------------------------
                    logger.info("User %s marked as verified in table %s", email, role_name)
                    return True

            # ---------------------------- User Not Found or Already Verified ----------------------------
            return False

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            logger.error("Error marking user verified:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
# Singleton instance to handle user verification operations
user_verification_service = UserVerificationService()

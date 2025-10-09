# ---------------------------- External Imports ----------------------------
# Capture full exception stack traces for debugging
import traceback

# ---------------------------- Internal Imports ----------------------------
# Role tables for looking up users and updating verification status
from ...access_control.role_tables import ROLE_TABLES

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- User Verification Service Class ----------------------------
# Service to handle marking users as verified
class UserVerificationService:
    """
    1. mark_user_verified - Mark a user as verified across role tables.
    """

    # ---------------------------- Mark User Verified ----------------------------
    # Static method to mark a user as verified in the database
    @staticmethod
    async def mark_user_verified(email: str, db) -> bool:
        """
        Input:
            1. email (str): Email of the user to verify.
            2. db (AsyncSession): Database session for operations.

        Process:
            1. Iterate over all role tables to locate the user.
            2. Fetch user using CRUD with db session.
            3. Check if user exists and is not already verified.
            4. Update 'is_verified' field to True in the database for that user.
            5. Return True indicating successful verification ,else false.

        Output:
            1. bool: True if verification succeeded, False otherwise.
        """
        try:
            # Step 1: Iterate over all role tables to locate the user
            for role_name, crud in ROLE_TABLES.items():
                # Step 2: Fetch user record from table using db session
                user = await crud.get_by_email(email, db)

                # Step 3: Check if user exists and is not already verified
                if user and not getattr(user, "is_verified", False):
                    # Step 4: Update 'is_verified' field to True
                    await crud.update_by_email(email, {"is_verified": True}, db)

                    # Log the verification action for auditing
                    logger.info("User %s marked as verified in table %s", email, role_name)

                    # Step 5: Return True indicating successful verification ,else false
                    return True

            # Return False if user was not found or already verified
            return False

        # Catch all unexpected exceptions during verification
        except Exception:
            # Log the full traceback for debugging purposes
            logger.error("Error marking user verified:\n%s", traceback.format_exc())
            return False


# ---------------------------- Service Instance ----------------------------
# Singleton instance to handle user verification operations
user_verification_service = UserVerificationService()

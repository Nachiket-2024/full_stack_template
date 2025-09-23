# ---------------------------- External Imports ----------------------------
# Logging for tracking events, warnings, and errors during signup
import logging

# Capture full exception stack traces for debugging
import traceback

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Role-based CRUD tables and default role for assigning new users
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# Password service for hashing passwords and validating strength
from ..password_logic.password_service import password_service

# ---------------------------- Logger Setup ----------------------------
# Configure module-specific logger for structured logging
logger = logging.getLogger(__name__)

# ---------------------------- Signup Service Class ----------------------------
# Service class to handle user signup logic
class SignupService:
    """
    1. signup - Validate input, hash password, check duplicates, and create user with default role.
    """

    # ---------------------------- Static Async Signup Method ----------------------------
    @staticmethod
    async def signup(name: str, email: str, password: str, db: AsyncSession = None) -> bool:
        """
        Input:
            1. name (str): Full name of the new user.
            2. email (str): Email address of the new user.
            3. password (str): Plaintext password.
            4. db (AsyncSession): Async database session for DB operations.

        Process:
            1. Validate password strength using password service.
            2. Check if user with same email already exists across all roles.
            3. Hash the password securely.
            4. Assign default role to the new user.
            5. Prepare user data dictionary for insertion.
            6. Insert new user into the default role table.
            7. Return True if user created successfully.

        Output:
            1. bool: True if user created successfully, False otherwise.
        """
        try:
            # Step 1: Validate password strength using password service
            if not await password_service.validate_password_strength(password):
                logger.warning("Weak password during signup for email: %s", email)
                return False

            # Step 2: Check if user with same email already exists across all roles
            for crud in ROLE_TABLES.values():
                if await crud.get_by_email(email, db=db):
                    logger.info("Signup attempt with existing email: %s", email)
                    return False

            # Step 3: Hash the password securely
            hashed_password = await password_service.hash_password(password)

            # Step 4: Assign default role to the new user
            role = DEFAULT_ROLE

            # Step 5: Prepare user data dictionary for insertion
            user_data = {
                "name": name,                       # User's full name
                "email": email,                     # User's email
                "hashed_password": hashed_password, # Secure hashed password
                "is_verified": False                # New users start as unverified
            }

            # Step 6: Insert user record into the default role table
            await ROLE_TABLES[role].create(user_data, db=db)

            # Step 7: Return true if user created successfully
            return True

        except Exception:
            # Log full exception stack trace
            logger.error("Error during signup:\n%s", traceback.format_exc())
            return False


# ---------------------------- Instantiate SignupService ----------------------------
# Singleton instance to handle signup operations
signup_service = SignupService()

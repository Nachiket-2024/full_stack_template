# ---------------------------- External Imports ----------------------------
# Capture full exception stack traces for debugging
import traceback

# Async SQLAlchemy session for database operations
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------- Internal Imports ----------------------------
# Role-based CRUD tables for creating users in the corresponding role table
from ...access_control.role_tables import ROLE_TABLES

# Password service for hashing passwords
from ..password_logic.password_service import password_service

# Import centralized logger factory to create structured, module-specific loggers
from ...logging.logging_config import get_logger

# ---------------------------- Logger Setup ----------------------------
# Create a logger instance for this module
logger = get_logger(__name__)

# ---------------------------- Signup Service Class ----------------------------
# Service class to handle user signup logic
class SignupService:
    """
    1. signup - Hash password, check duplicates, and create user in specified role.
    """

    # ---------------------------- Static Async Signup Method ----------------------------
    @staticmethod
    async def signup(name: str, email: str, password: str, role: str, db: AsyncSession = None) -> bool:
        """
        Input:
            1. name (str): Full name of the new user.
            2. email (str): Email address of the new user.
            3. password (str): Plaintext password.
            4. role (str): Role under which the user should be created.
            5. db (AsyncSession): Async database session for DB operations.

        Process:
            1. Check if user with same email already exists across all roles.
            2. Hash the password securely.
            3. Prepare user data dictionary for insertion.
            4. Insert new user into the specified role table.
            5. Return True if user created successfully.

        Output:
            1. bool: True if user created successfully, False otherwise.
        """
        try:
            # Step 1: Check if user with same email already exists across all roles
            for crud in ROLE_TABLES.values():
                if await crud.get_by_email(email, db=db):
                    logger.info("Signup attempt with existing email: %s", email)
                    return False

            # Step 2: Hash the password securely
            hashed_password = await password_service.hash_password(password)

            # Step 3: Prepare user data dictionary for insertion
            user_data = {
                "name": name,                       # User's full name
                "email": email,                     # User's email
                "hashed_password": hashed_password, # Secure hashed password
                "is_verified": False                # New users start as unverified
            }

            # Step 4: Insert user record into the specified role table
            await ROLE_TABLES[role].create(user_data, db=db)

            # Step 5: Return true if user created successfully
            return True

        except Exception:
            # Log full exception stack trace
            logger.error("Error during signup:\n%s", traceback.format_exc())
            return False


# ---------------------------- Instantiate SignupService ----------------------------
# Singleton instance to handle signup operations
signup_service = SignupService()

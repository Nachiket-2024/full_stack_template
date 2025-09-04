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
    1. signup - Validate input, hash password, check duplicates, and create user.
    """

    # ---------------------------- Static Async Signup Method ----------------------------
    @staticmethod
    async def signup(name: str, email: str, password: str, role: str | None = None, db: AsyncSession = None) -> bool:
        """
        Input:
            1. name (str): Full name of the new user.
            2. email (str): Email address of the new user.
            3. password (str): Plaintext password.
            4. role (str | None): Role to assign; defaults to default role.
            5. db (AsyncSession): Async database session for DB operations.

        Process:
            1. Validate password strength using password service.
            2. Check if user with same email already exists across all roles.
            3. Hash the password securely.
            4. Assign role (or default role if none provided).
            5. Prepare user data dictionary and create user in DB.

        Output:
            1. bool: True if user created successfully, False otherwise.
        """
        try:
            # ---------------------------- Validate Password Strength ----------------------------
            # Return False if password does not meet security requirements
            if not await password_service.validate_password_strength(password):
                logger.warning("Weak password during signup for email: %s", email)
                return False

            # ---------------------------- Check for Existing Users ----------------------------
            # Loop over all role tables to check if email already exists
            for crud in ROLE_TABLES.values():
                if await crud.get_by_email(email, db=db):
                    logger.info("Signup attempt with existing email: %s", email)
                    return False

            # ---------------------------- Hash Password ----------------------------
            # Generate secure hash of the password
            hashed_password = await password_service.hash_password(password)

            # ---------------------------- Assign Role ----------------------------
            # Use provided role or fallback to default role
            role = role or DEFAULT_ROLE

            # Validate role exists in ROLE_TABLES
            if role not in ROLE_TABLES:
                logger.warning("Invalid role during signup: %s", role)
                return False

            # ---------------------------- Prepare User Data ----------------------------
            # Construct dictionary for new user record
            user_data = {
                "name": name,                     # User's full name
                "email": email,                   # User's email
                "hashed_password": hashed_password,  # Secure hashed password
                "is_verified": False              # New users start as unverified
            }

            # ---------------------------- Create User in DB ----------------------------
            # Use appropriate role table to insert user record
            await ROLE_TABLES[role].create(user_data, db=db)
            logger.info("User %s created with role %s", email, role)
            return True

        # ---------------------------- Exception Handling ----------------------------
        except Exception:
            # Log full exception stack trace
            logger.error("Error during signup:\n%s", traceback.format_exc())
            return False


# ---------------------------- Instantiate SignupService ----------------------------
# Singleton instance to handle signup operations
signup_service = SignupService()

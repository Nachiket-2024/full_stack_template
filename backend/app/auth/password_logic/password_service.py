# ---------------------------- External Imports ----------------------------
# Password hashing library with Argon2 support for secure password storage
from passlib.context import CryptContext

# Modules for handling date and time calculations
from datetime import datetime, timedelta, timezone

# JWT library for encoding and decoding JSON Web Tokens
import jwt

# Regular expression module for validating password strength
import re

# ---------------------------- Internal Imports ----------------------------
# Application settings including SECRET_KEY and JWT configurations
from ...core.settings import settings

# Role tables and default role definitions for user management
from ...access_control.role_tables import ROLE_TABLES, DEFAULT_ROLE

# ---------------------------- Password Context ----------------------------
# Configure password hashing using Argon2id algorithm
pwd_context = CryptContext(
    schemes=["argon2"],  # Use Argon2 hashing scheme
    deprecated="auto"    # Automatically handle deprecated hashes
)

# ---------------------------- Password Service ----------------------------
# Service class handling password hashing, verification, and reset tokens
class PasswordService:
    """
    1. hash_password: Hash a plain password.
    2. verify_password: Compare plain and hashed passwords.
    3. validate_password_strength: Check password complexity.
    4. create_reset_token: Generate JWT for password reset.
    5. verify_reset_token: Decode and validate reset JWT.
    """

    # ---------------------------- Hash Password ----------------------------
    # Static method to hash a plain password
    @staticmethod
    async def hash_password(password: str) -> str:
        """
        Input:
            1. password (str): Plain password string to be hashed.

        Process:
            1. Hash the password using pwd_context with Argon2.

        Output:
            1. str: Hashed password string.
        """
        # Step 1: Hash the password using pwd_context with Argon2
        return pwd_context.hash(password)

    # ---------------------------- Verify Password ----------------------------
    # Static method to verify a plain password against a hashed password
    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Input:
            1. plain_password (str): Plain password to verify.
            2. hashed_password (str): Hashed password to compare against.

        Process:
            1. Verify the plain password against the hashed password using pwd_context.

        Output:
            1. bool: True if passwords match, False otherwise.
        """
        # Step 1: Verify the plain password against the hashed password using pwd_context
        return pwd_context.verify(plain_password, hashed_password)

    # ---------------------------- Validate Password Strength ----------------------------
    # Static method to validate password complexity requirements
    @staticmethod
    async def validate_password_strength(password: str) -> bool:
        """
        Input:
            1. password (str): Password string to validate.

        Process:
            1. Check if length is at least 8 characters.
            2. Ensure it contains at least one digit.
            3. Ensure it contains at least one special character.
            4. Return True if it passes all checks.

        Output:
            1. bool: True if password passes all checks, False otherwise.
        """
        # Step 1: Check if length is at least 8 characters
        if len(password) < 8:
            return False
        
        # Step 2: Ensure it contains at least one digit
        if not re.search(r"\d", password):
            return False
        
        # Step 3: Ensure it contains at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        
        # Step 4: Return True if it passes all checks
        return True

    # ---------------------------- Create Reset Token ----------------------------
    # Static method to create a JWT for password reset
    @staticmethod
    async def create_reset_token(email: str, 
                                 role: str | None = None, 
                                 expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES
                                 ) -> str:
        """
        Input:
            1. email (str): Email of the user requesting reset.
            2. role (str | None): User role; defaults to DEFAULT_ROLE if None.
            3. expires_minutes (int): Expiration time in minutes for token.

        Process:
            1. Assign default role if role is None.
            2. Validate role exists in ROLE_TABLES.
            3. Calculate expiration timestamp in UTC.
            4. Create payload with email, role, and expiration.
            5. Encode JWT using SECRET_KEY and JWT_ALGORITHM.

        Output:
            1. str: Encoded JWT token string.
        """
        # Step 1: Assign default role if role is None
        if role is None:
            role = DEFAULT_ROLE

        # Step 2: Validate role exists in ROLE_TABLES
        if role not in ROLE_TABLES:
            raise ValueError(f"Invalid role for reset token: {role}")

        # Step 3: Calculate expiration timestamp in UTC
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        # Step 4: Create payload with email, role, and expiration
        payload: dict[str, str | float] = {
            "email": email,
            "role": role,
            "exp": expire.timestamp()
        }

        # Step 5: Encode JWT using SECRET_KEY and JWT_ALGORITHM
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return token

    # ---------------------------- Verify Reset Token ----------------------------
    # Static method to decode and verify a password reset JWT
    @staticmethod
    async def verify_reset_token(token: str) -> dict | None:
        """
        Input:
            1. token (str): JWT token string to verify.

        Process:
            1. Decode JWT using SECRET_KEY and JWT_ALGORITHM.
            2. Validate that role in payload exists in ROLE_TABLES.
            3. Return payload if valid

        Output:
            1. dict | None: Payload dict if valid, None if invalid or expired.
        """
        try:
            # Step 1: Decode JWT using SECRET_KEY and JWT_ALGORITHM
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # Step 2: Validate that role in payload exists in ROLE_TABLES
            if payload.get("role") not in ROLE_TABLES:
                return None
            
            # Step 3: Return payload if valid
            return payload
        
        except jwt.ExpiredSignatureError:
            # Token expired
            return None
        
        except jwt.InvalidTokenError:
            # Token invalid
            return None


# ---------------------------- Service Instance ----------------------------
# Single global instance of PasswordService
password_service = PasswordService()

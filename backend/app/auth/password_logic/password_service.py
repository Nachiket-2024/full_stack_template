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
# Service class for password operations: hashing, verification, validation, and reset tokens
class PasswordService:

    # ---------------------------- Hash Password ----------------------------
    # Generate a hashed password asynchronously
    @staticmethod
    async def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    # ---------------------------- Verify Password ----------------------------
    # Check if a plain password matches a hashed password asynchronously
    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # ---------------------------- Validate Password Strength ----------------------------
    # Ensure password meets minimum security requirements asynchronously
    @staticmethod
    async def validate_password_strength(password: str) -> bool:

        # Minimum length 8 characters
        if len(password) < 8:
            return False
        # Must contain at least one digit
        if not re.search(r"\d", password):
            return False
        # Must contain at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    # ---------------------------- Create Reset Token ----------------------------
    # Generate a JWT token for password reset asynchronously
    @staticmethod
    async def create_reset_token(email: str, 
                                 role: str | None = None, 
                                 expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES
                                 ) -> str:

        # Use default role if none is provided
        if role is None:
            role = DEFAULT_ROLE

        # Ensure the role exists in ROLE_TABLES
        if role not in ROLE_TABLES:
            raise ValueError(f"Invalid role for reset token: {role}")

        # Calculate expiration timestamp in UTC
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        # Prepare token payload with email, role, and expiration
        payload: dict[str, str | float] = {
            "email": email,
            "role": role,
            "exp": expire.timestamp()
        }

        # Encode the payload as a JWT
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------- Verify Reset Token ----------------------------
    # Decode and validate a password reset JWT asynchronously
    @staticmethod
    async def verify_reset_token(token: str) -> dict | None:

        try:
            # Decode JWT using the secret key and allowed algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            # Ensure the role in the payload is valid
            if payload.get("role") not in ROLE_TABLES:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None


# ---------------------------- Service Instance ----------------------------
# Single global instance of the PasswordService for use in other modules
password_service = PasswordService()

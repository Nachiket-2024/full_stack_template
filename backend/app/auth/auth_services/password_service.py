# ---------------------------- External Imports ----------------------------
# Password hashing library with Argon2 support
from passlib.context import CryptContext

# For datetime calculations
from datetime import datetime, timedelta, timezone

# JWT encoding/decoding
import jwt

# ---------------------------- Internal Imports ----------------------------
# Load settings like SECRET_KEY from core
from ...core.settings import settings

# Centralized role table and default role
from ...core.role_tables import ROLE_TABLES, DEFAULT_ROLE

# ---------------------------- Password Context ----------------------------
# Use Argon2id for hashing: highly secure and future-proof
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# ---------------------------- Password Service ----------------------------
class PasswordService:
    """
    Service to handle password hashing, verification, and reset tokens.
    Uses Argon2id for secure hashing.
    """

    # ---------------------------- Hash Password ----------------------------
    @staticmethod
    async def hash_password(password: str) -> str:
        """
        Hash plain password asynchronously using Argon2id.
        """
        return pwd_context.hash(password)

    # ---------------------------- Verify Password ----------------------------
    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against the stored Argon2 hash.
        """
        return pwd_context.verify(plain_password, hashed_password)

    # ---------------------------- Validate Password Strength ----------------------------
    @staticmethod
    async def validate_password_strength(password: str) -> bool:
        """
        Check password strength: minimum 8 chars, at least one number, one symbol.
        """
        import re
        if len(password) < 8:
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    # ---------------------------- Create Reset Token ----------------------------
    @staticmethod
    async def create_reset_token(email: str, role: str | None = None, expires_minutes: int = settings.RESET_TOKEN_EXPIRE_MINUTES) -> str:
        """
        Generate a short-lived JWT for password reset.
        Uses default role if none is provided.
        """
        if role is None:
            role = DEFAULT_ROLE

        # Ensure role exists
        if role not in ROLE_TABLES:
            raise ValueError(f"Invalid role for reset token: {role}")

        # Calculate expiration timestamp
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        # Prepare payload with minimal info
        payload: dict[str, str | float] = {
            "sub": email,
            "role": role,
            "exp": expire.timestamp()
        }

        # Encode JWT
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------- Verify Reset Token ----------------------------
    @staticmethod
    async def verify_reset_token(token: str) -> dict | None:
        """
        Verify reset token. Returns payload if valid, None otherwise.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("role") not in ROLE_TABLES:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
password_service = PasswordService()

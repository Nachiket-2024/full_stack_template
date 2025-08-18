# ---------------------------- External Imports ----------------------------
# For hashing passwords securely
from passlib.context import CryptContext

# For creating and decoding JWT tokens
import jwt
from datetime import datetime, timedelta

# For OAuth2 password flow and FastAPI security
from fastapi.security import OAuth2PasswordBearer

# ---------------------------- Internal Imports ----------------------------
from .settings import settings  # Load app settings (JWT secret, expiration times, etc.)

# ---------------------------- Password Hashing ----------------------------
# Use bcrypt hashing scheme for passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a plain password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify a plain password against its hashed version
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------------- JWT Token Helpers ----------------------------
# OAuth2 password bearer for dependency injection in routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Create a JWT access token
def create_access_token(data: dict, expires_delta: int = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Decode and verify a JWT token
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None

# ---------------------------- Google OAuth2 Helpers ----------------------------
# These can be used in your auth routes to handle Google OAuth2 flow
from google_auth_oauthlib.flow import Flow

def get_google_flow() -> Flow:
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
                "redirect_uris": [settings.GMAIL_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["openid", "email", "profile"]
    )

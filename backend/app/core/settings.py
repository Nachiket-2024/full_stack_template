# ---------------------------- External Imports ----------------------------
# Pydantic's BaseSettings allows loading environment variables from .env
from pydantic_settings import BaseSettings

# ---------------------------- Settings Class ----------------------------
# Load configuration from .env file and provide structured access
class Settings(BaseSettings):

    BACKEND_BASE_URL: str                           # Backend URL for Auth redirection from frontend
    FRONTEND_BASE_URL: str                          # Frontend URL for redirection

    DATABASE_URL: str                               # Async PostgreSQL connection URL
    POSTGRES_USER: str                              # PostgreSQL username
    POSTGRES_PASSWORD: str                          # PostgreSQL password
    POSTGRES_DB: str                                # PostgreSQL DB name

    SECRET_KEY: str                                 # Secret key for JWT encoding
    ACCESS_TOKEN_EXPIRE_MINUTES: int                # Access token expiration time in minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int               # Refresh token expiration time in minutes
    JWT_ALGORITHM: str                              # Algorithm for JWT encoding
    RESET_TOKEN_EXPIRE_MINUTES: int                 # Password reset token expiration time in minutes

    GOOGLE_CLIENT_ID: str                           # OAuth2 Client ID for Gmail
    GOOGLE_CLIENT_SECRET: str                       # OAuth2 Client Secret for Gmail
    GOOGLE_REDIRECT_URI: str                        # OAuth2 redirect URI for Gmail login

    REDIS_URL: str                                  # Redis connection URL
    CACHE_DEFAULT_TTL: int                          # Default TTL for Redis cache keys in seconds

    FROM_EMAIL: str                                 # Email address used to send password reset emails
    GMAIL_APP_PASSWORD: str                         # Gmail App password for sending email from above account

    LOGIN_LOCKOUT_TIME: int                         # Time in seconds to lockout after failed login attempts
    MAX_FAILED_LOGIN_ATTEMPTS: int                  # Max failed login attempts before lockout
    MAX_REQUESTS_PER_WINDOW: int                    # Max requests allowed per rate limit window
    REQUEST_WINDOW_SECONDS: int                     # Time window for rate limiting in seconds

    class Config:
        # Load environment variables from a .env file
        env_file = ".env"

        # Encoding for the .env file
        env_file_encoding = "utf-8"


# ---------------------------- Settings Instance ----------------------------
# Create a single settings instance for global use across the app
settings = Settings()

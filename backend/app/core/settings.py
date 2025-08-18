# ---------------------------- External Imports ----------------------------
# Pydantic's BaseSettings allows loading environment variables from .env
from pydantic import BaseSettings

# ---------------------------- Settings Class ----------------------------
# Load configuration from .env file and provide structured access
class Settings(BaseSettings):
    # ---------------------------- App Config ----------------------------
    APP_NAME: str                                   # Name of the application
    DEBUG: bool                                     # Enable debug mode

    # ---------------------------- Database Config ----------------------------
    DATABASE_URL: str                               # Async PostgreSQL connection URL

    # ---------------------------- JWT Config ----------------------------
    SECRET_KEY: str                                 # Secret key for JWT encoding
    ACCESS_TOKEN_EXPIRE_MINUTES: int                # Access token expiration time in minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int               # Refresh token expiration time in minutes

    # ---------------------------- OAuth2 / Gmail Config ----------------------------
    GMAIL_CLIENT_ID: str
    GMAIL_CLIENT_SECRET: str
    GMAIL_REDIRECT_URI: str

    # ---------------------------- Redis Config ----------------------------
    REDIS_URL: str                                  # Redis connection URL

    # ---------------------------- Celery Config ----------------------------
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # ---------------------------- Pydantic Config ----------------------------
    class Config:
        # Load environment variables from a .env file
        env_file = ".env"
        env_file_encoding = "utf-8"

# ---------------------------- Settings Instance ----------------------------
# Create a single settings instance for global use across the app
settings = Settings()

# ---------------------------- External Imports ----------------------------
# Async Redis client
from redis.asyncio import Redis

# ---------------------------- Internal Imports ----------------------------
# App settings including REDIS_URL
from ..core.settings import settings

# ---------------------------- Redis Client ----------------------------
# Create a single async connection pool for Redis
redis_client = Redis.from_url(
    settings.REDIS_URL,       # e.g., redis://localhost:6379/0
    decode_responses=True     # Return strings instead of bytes
)

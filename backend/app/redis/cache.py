# ---------------------------- Internal Imports ----------------------------
# Async Redis client
from .client import redis_client

# ---------------------------- Cache Service ----------------------------
class CacheService:
    """
    Service to handle simple key-value caching in Redis.
    """

    # ---------------------------- Set Cache ----------------------------
    # Input: key string, value string, optional expiration in seconds
    # Output: None
    @staticmethod
    async def set_cache(key: str, value: str, expire: int = 300) -> None:
        """
        Store a key-value pair in Redis with optional TTL.
        """
        await redis_client.set(key, value, ex=expire)

    # ---------------------------- Get Cache ----------------------------
    # Input: key string
    # Output: value string if exists, else None
    @staticmethod
    async def get_cache(key: str) -> str | None:
        """
        Retrieve a value from Redis by key.
        """
        return await redis_client.get(key)

# ---------------------------- Service Instance ----------------------------
# Single instance for global use
cache_service = CacheService()

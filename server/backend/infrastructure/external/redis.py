"""Redis client using redis-py for caching, pubsub, and notifications."""

import asyncio
import json
import time
from typing import Any

import redis.asyncio as redis
import structlog
from redis.asyncio import ConnectionPool

from ...core.app import settings

logger = structlog.get_logger()


def _json_serializer(obj: Any) -> str:
    """Serialize UUID and datetime objects to JSON strings."""
    from datetime import datetime
    from uuid import UUID

    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(
        f"Object of type {type(obj).__name__} is not JSON serializable"
    )


_redis_pool: ConnectionPool | None = None
_redis_client: redis.Redis | None = None
_last_failed_at: float | None = None
_RETRY_COOLDOWN_SECONDS = 30


async def get_redis_client() -> redis.Redis:
    """Get the global Redis client.

    Uses redis-py async client.
    Supports caching, pub/sub for SSE notifications.

    Returns:
        The Redis client instance.

    Raises:
        Exception: If connection fails.

    """
    global _redis_client, _redis_pool, _last_failed_at

    if _last_failed_at is not None:
        time_since_failure = time.time() - _last_failed_at
        if time_since_failure < _RETRY_COOLDOWN_SECONDS:
            if settings.environment.lower() == "production":
                remaining_cooldown = (
                    _RETRY_COOLDOWN_SECONDS - time_since_failure
                )
                raise Exception(
                    f"Redis connection failed recently. Retry available in {int(remaining_cooldown)}s."
                )

    if _redis_client is None:
        logger.info(
            "Initializing Redis client",
            url=settings.redis_url,
        )
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            retry_on_timeout=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
            socket_keepalive=True,
            health_check_interval=30,
        )
        _redis_client = redis.Redis(connection_pool=_redis_pool)

        try:
            await asyncio.wait_for(_redis_client.ping(), timeout=3.0)
            logger.info("Redis connected successfully")
            _last_failed_at = None
        except TimeoutError:
            logger.exception("Redis connection timed out after 3 seconds")
            _last_failed_at = time.time()
            _redis_client = None
            _redis_pool = None
            raise
        except Exception as e:
            logger.exception("Failed to connect to Redis", error=str(e))
            _last_failed_at = time.time()
            _redis_client = None
            _redis_pool = None
            raise

    return _redis_client


async def close_redis() -> None:
    """Close the Redis client and connection pool.

    This should be called during application shutdown.
    """
    global _redis_client, _redis_pool

    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
        _redis_client = None
        logger.info("Redis connection closed")


class RedisCache:
    """Redis cache wrapper."""

    def __init__(self, redis_client: redis.Redis) -> None:
        """Initialize the Redis cache wrapper.

        Args:
            redis_client: Redis client instance.

        """
        self.redis = redis_client

    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        try:
            value = await self.redis.get(key)
            if value is not None:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Redis get failed", key=key, error=str(e))
            return None

    async def set(
        self, key: str, value: Any, expire: int | None = None
    ) -> bool:
        """Set a value in cache with optional expiration."""
        try:
            serialized = json.dumps(value, default=_json_serializer)
            await self.redis.set(key, serialized, ex=expire)
            return True
        except Exception as e:
            logger.warning("Redis set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning("Redis delete failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.warning("Redis exists failed", key=key, error=str(e))
            return False

    async def get_keys_by_pattern(self, pattern: str) -> list[str]:
        """Get keys matching a pattern."""
        try:
            keys = await self.redis.keys(pattern)
            return [
                key.decode() if isinstance(key, bytes) else key for key in keys
            ]
        except Exception as e:
            logger.warning(
                "Redis get_keys_by_pattern failed",
                pattern=pattern,
                error=str(e),
            )
            return []

    async def delete_multiple(self, keys: list[str]) -> int:
        """Delete multiple keys."""
        try:
            if not keys:
                return 0
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.warning(
                "Redis delete_multiple failed", keys=keys, error=str(e)
            )
            return 0


_cache: RedisCache | None = None


async def get_cache() -> RedisCache:
    """Get the global Redis cache instance."""
    global _cache
    if _cache is None:
        redis_client = await get_redis_client()
        _cache = RedisCache(redis_client)
    return _cache

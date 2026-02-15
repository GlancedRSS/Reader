"""Arq client for enqueuing background jobs."""

import uuid
from datetime import UTC, datetime
from typing import Any

from arq import create_pool
from arq.connections import RedisSettings
from structlog import get_logger

from backend.core.app import settings
from backend.infrastructure.external.redis import get_cache

logger = get_logger(__name__)

JOB_TTL = 3600


def _parse_redis_url(redis_url: str) -> tuple[str, int]:
    """Parse Redis URL to extract host and port.

    Args:
        redis_url: Redis URL (e.g., "redis://localhost:6379" or "redis://host:port").

    Returns:
        Tuple of (host, port).

    """
    if redis_url.startswith("redis://"):
        redis_url = redis_url[8:]

    if ":" in redis_url:
        host, port = redis_url.split(":")
        return host, int(port)
    return redis_url, 6379


class ArqClient:
    """Client for enqueuing jobs with Arq."""

    _pool: Any | None

    def __init__(self) -> None:
        """Initialize the Arq client.

        Note: Actual connection is created lazily when needed.
        """
        self._redis_settings = self._get_redis_settings()
        self._pool = None

    def _get_redis_settings(self) -> RedisSettings:
        """Get Redis settings for Arq connection.

        Returns:
            RedisSettings instance.

        """
        redis_url = settings.redis_url or "redis://localhost:6379"
        host, port = _parse_redis_url(redis_url)
        return RedisSettings(host=host, port=port)

    async def _get_pool(self) -> Any:
        """Get or create Redis pool connection.

        Returns:
            Arq Redis pool.

        """
        if self._pool is None:
            self._pool = await create_pool(self._redis_settings)
        return self._pool

    async def enqueue_job(
        self,
        function_name: str,
        job_name: str | None = None,
        queue_name: str | None = None,
        job_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Enqueue a job to be processed by Arq worker.

        Args:
            function_name: Name of the function to call (e.g., "opml_import").
            job_name: Optional name for the job (for logging).
            queue_name: Optional queue name (defaults to "arq:queue").
            job_id: Optional specific job ID to use.
            **kwargs: Keyword arguments to pass to the job function.

        Returns:
            Job ID (UUID string).

        Raises:
            ValueError: If required parameters are missing.

        """
        job_id = job_id or str(uuid.uuid4())

        pool = await self._get_pool()

        await pool.enqueue_job(
            function_name,
            _job_id=job_id,
            **kwargs,
        )

        logger.info(
            "Job enqueued with Arq",
            job_id=job_id,
            function_name=function_name,
            job_name=job_name,
        )

        return job_id

    async def close(self) -> None:
        """Close the Redis pool connection."""
        if self._pool:
            await self._pool.close()
            self._pool = None


class JobTracker:
    """Utility for tracking job status in Redis.

    Jobs are stored in Redis and can be polled for status.
    """

    @staticmethod
    async def create_job_record(
        job_id: str, job_type: str, payload: dict[str, Any]
    ) -> None:
        """Create a job record in Redis.

        Args:
            job_id: The job ID.
            job_type: The job type.
            payload: The job payload.

        """
        job = {
            "job_id": job_id,
            "job_type": job_type,
            "status": "pending",
            "payload": payload,
            "result": None,
            "error": None,
            "created_at": datetime.now(UTC),
            "completed_at": None,
        }

        cache = await get_cache()
        await cache.set(f"job:{job_id}", job, expire=JOB_TTL)

    @staticmethod
    async def update_job(
        job_id: str,
        status: str,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """Update job status in Redis.

        Args:
            job_id: The job ID.
            status: The new status.
            result: Optional result data.
            error: Optional error message.

        """
        cache = await get_cache()
        job = await cache.get(f"job:{job_id}")

        if not job:
            logger.warning(
                "Attempted to update non-existent job", job_id=job_id
            )
            return

        job["status"] = status
        job["result"] = result
        job["error"] = error
        job["completed_at"] = datetime.now(UTC)

        await cache.set(f"job:{job_id}", job, expire=JOB_TTL)

    @staticmethod
    async def get_job(job_id: str) -> dict[str, Any] | None:
        """Get job by ID from Redis.

        Args:
            job_id: The job ID.

        Returns:
            Job data or None if not found.

        """
        cache = await get_cache()
        return await cache.get(f"job:{job_id}")

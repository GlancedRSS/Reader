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


class ArqClient:
    _pool: Any | None

    def __init__(self) -> None:
        self._redis_settings = self._get_redis_settings()
        self._pool = None

    def _get_redis_settings(self) -> RedisSettings:
        redis_url = settings.redis_url or "redis://localhost:6379"
        return RedisSettings.from_dsn(redis_url)

    async def _get_pool(self) -> Any:
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
        if self._pool:
            await self._pool.close()
            self._pool = None


class JobTracker:
    @staticmethod
    async def create_job_record(
        job_id: str, job_type: str, payload: dict[str, Any]
    ) -> None:
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
        cache = await get_cache()
        return await cache.get(f"job:{job_id}")

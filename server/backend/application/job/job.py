"""Application service for job management."""

from datetime import UTC, datetime
from typing import Any

import structlog

from backend.infrastructure.external.redis import get_cache

logger = structlog.get_logger(__name__)

JOB_TTL = 3600


class JobApplication:
    """Application service for job management via Redis."""

    async def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Get job by ID from Redis."""
        cache = await get_cache()
        return await cache.get(f"job:{job_id}")

    async def update_job(
        self,
        job_id: str,
        status: str,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """Update job status in Redis."""
        job = await self.get_job(job_id)
        if not job:
            logger.warning(
                "Attempted to update non-existent job", job_id=job_id
            )
            return

        job["status"] = status
        job["result"] = result
        job["error"] = error
        job["completed_at"] = datetime.now(UTC)

        cache = await get_cache()
        await cache.set(f"job:{job_id}", job, expire=JOB_TTL)

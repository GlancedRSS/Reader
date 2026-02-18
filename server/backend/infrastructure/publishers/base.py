"""Base publisher for job-related operations."""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from backend.core.app import settings
from backend.infrastructure.external.arq_client import ArqClient
from backend.infrastructure.external.redis import get_cache

logger = structlog.get_logger()

JOB_TTL = 3600


class BaseJobPublisher:
    """Base publisher for job-related operations."""

    def __init__(self, arq_client: ArqClient | None = None) -> None:
        """Initialize the base job publisher."""
        self._arq_client = arq_client
        self._api_base_url = settings.api_base_url

    async def _create_job_record(
        self, job_id: str, job_type: str, payload: dict[str, Any]
    ) -> None:
        """Create a job record in Redis."""
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

    async def _create_and_publish_job(
        self,
        job_type: str,
        arq_function: str,
        payload: dict[str, Any],
        deduplication_key: str | None = None,
        delay_seconds: int = 0,
        retries: int = 3,
    ) -> dict[str, Any]:
        """Create a job record and publish to worker via Arq."""
        job_id = str(uuid.uuid4())

        await self._create_job_record(
            job_id=job_id,
            job_type=job_type,
            payload=payload,
        )

        logger.info(
            "Publishing job to Arq worker",
            job_id=job_id,
            job_type=job_type,
            arq_function=arq_function,
        )

        client = self._arq_client or ArqClient()
        await client.enqueue_job(
            function_name=arq_function,
            job_name=job_type,
            job_id=job_id,
            _defer_by=delay_seconds,
            **payload,
        )

        return {
            "job_id": job_id,
        }

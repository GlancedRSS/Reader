"""Publisher for discovery-related background jobs."""

from typing import Any
from uuid import UUID

from backend.core.app import settings
from backend.infrastructure.publishers.base import BaseJobPublisher


class DiscoveryPublisher(BaseJobPublisher):
    """Publisher for feed onboarding jobs (create and subscribe to new feeds)."""

    async def publish_create_and_subscribe_with_job(
        self,
        url: str,
        user_id: UUID,
        folder_id: UUID | None = None,
        delay_seconds: int = 0,
    ) -> dict[str, Any]:
        """Create job and publish feed creation + subscription to worker."""
        payload = {
            "url": url,
            "user_id": str(user_id),
            "folder_id": str(folder_id) if folder_id else None,
        }

        if folder_id:
            payload["folder_id"] = str(folder_id)

        if settings.environment == "development" or delay_seconds > 0:
            dedup_key = None
        else:
            dedup_key = f"create_subscribe:{user_id}:{url}"

        return await self._create_and_publish_job(
            job_type="feed_create_and_subscribe",
            arq_function="feed_create_and_subscribe",
            payload=payload,
            deduplication_key=dedup_key,
            delay_seconds=delay_seconds,
            retries=0,
        )

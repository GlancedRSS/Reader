"""Auto-mark read job handlers.

This module contains handlers for auto-marking articles as read
based on user preferences (7/14/30 days).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from structlog import get_logger

from backend.infrastructure.jobs.base import BaseJobHandler
from backend.infrastructure.repositories.subscription import (
    SubscriptionRepository,
)
from backend.schemas.workers import (
    AutoMarkReadJobRequest,
    AutoMarkReadJobResponse,
)

logger = get_logger(__name__)


class AutoMarkReadJobHandler(
    BaseJobHandler[AutoMarkReadJobRequest, AutoMarkReadJobResponse]
):
    """Handler for auto-mark as read job.

    Marks old articles as read based on user preferences.
    Supports both all-users (bulk) and single-user modes.
    """

    def __init__(
        self,
        user_repository: Any,
        subscription_repository: SubscriptionRepository,
    ) -> None:
        """Initialize the handler.

        Args:
            user_repository: User repository for data access (single-user mode).
            subscription_repository: Subscription repository for article operations.

        """
        self._user_repo = user_repository
        self._subscription_repo = subscription_repository

    async def execute(
        self, request: AutoMarkReadJobRequest
    ) -> AutoMarkReadJobResponse:
        """Execute the auto-mark as read job.

        Args:
            request: The auto-mark read job request

        Returns:
            Response with processing statistics

        """
        logger.info(
            "Starting auto-mark as read",
            job_id=request.job_id,
            user_id=request.user_id or "all",
        )

        now = datetime.now(UTC)
        cutoff_date_7days = now - timedelta(days=7)
        cutoff_date_14days = now - timedelta(days=14)
        cutoff_date_30days = now - timedelta(days=30)

        if not request.user_id:
            result = (
                await self._subscription_repo.bulk_mark_old_articles_as_read(
                    cutoff_date_7days=cutoff_date_7days,
                    cutoff_date_14days=cutoff_date_14days,
                    cutoff_date_30days=cutoff_date_30days,
                )
            )

            users_skipped = 0
            users_processed = result["users_affected"]
            articles_marked_read = result["articles_marked"]

            logger.info(
                "Bulk auto-mark as read completed",
                job_id=request.job_id,
                users_processed=users_processed,
                articles_marked_read=articles_marked_read,
            )

            return AutoMarkReadJobResponse(
                job_id=request.job_id,
                status="success",
                message=f"Processed {users_processed} users, marked {articles_marked_read} articles",
                users_processed=users_processed,
                articles_marked_read=articles_marked_read,
                users_skipped=users_skipped,
            )

        user = await self._user_repo.get_user_by_id(request.user_id)
        if not user:
            return AutoMarkReadJobResponse(
                job_id=request.job_id,
                status="success",
                message="User not found",
                users_processed=0,
                articles_marked_read=0,
                users_skipped=0,
            )

        prefs = await self._user_repo.get_user_preferences(user.id)

        if not prefs or prefs.auto_mark_as_read == "disabled":
            return AutoMarkReadJobResponse(
                job_id=request.job_id,
                status="success",
                message="Auto-mark as read is disabled for this user",
                users_processed=0,
                articles_marked_read=0,
                users_skipped=1,
            )

        cutoff_days_map = {
            "7_days": 7,
            "14_days": 14,
            "30_days": 30,
        }
        cutoff_days = cutoff_days_map.get(prefs.auto_mark_as_read, 7)
        cutoff_date = now - timedelta(days=cutoff_days)

        unread_articles = (
            await self._subscription_repo.get_unread_articles_for_user(
                user.id, cutoff_date
            )
        )

        if not unread_articles:
            return AutoMarkReadJobResponse(
                job_id=request.job_id,
                status="success",
                message="No unread articles to mark",
                users_processed=0,
                articles_marked_read=0,
                users_skipped=1,
            )

        article_ids = [ua.article_id for ua in unread_articles]
        marked_count = await self._subscription_repo.mark_articles_as_read(
            user.id, article_ids
        )

        logger.info(
            "Single-user auto-mark as read completed",
            job_id=request.job_id,
            user_id=str(user.id),
            articles_marked=marked_count,
        )

        return AutoMarkReadJobResponse(
            job_id=request.job_id,
            status="success",
            message=f"Marked {marked_count} articles as read",
            users_processed=1,
            articles_marked_read=marked_count,
            users_skipped=0,
        )

"""Scheduled maintenance job handlers.

This module contains handlers for scheduled background jobs including
feed cleanup, OPML cleanup, and feed refresh cycle.
"""

import asyncio
import time
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import select
from structlog import get_logger

if TYPE_CHECKING:
    from backend.application.feed.feed import FeedApplication

from backend.core.database import AsyncSessionLocal
from backend.infrastructure.jobs.base import BaseJobHandler
from backend.infrastructure.repositories import (
    FeedRepository,
)
from backend.schemas.workers import (
    FeedCleanupJobRequest,
    FeedCleanupJobResponse,
    ScheduledFeedRefreshCycleJobRequest,
    ScheduledFeedRefreshCycleJobResponse,
)

logger = get_logger(__name__)


class FeedCleanupHandler:
    """Handler for feed cleanup job.

    Marks feeds as inactive when they have no subscribers.
    """

    async def execute(
        self, request: FeedCleanupJobRequest
    ) -> FeedCleanupJobResponse:
        """Execute the feed cleanup job.

        Finds feeds with zero UserFeed subscriptions and marks them inactive
        using a single bulk UPDATE query.

        Args:
            request: The feed cleanup job request

        Returns:
            Response with cleanup statistics

        """
        from backend.core.database import AsyncSessionLocal

        logger.info("Starting feed cleanup", job_id=request.job_id)

        async with AsyncSessionLocal() as db:
            feed_repo = FeedRepository(db)
            inactive_feeds = await feed_repo.bulk_mark_orphaned_feeds_inactive()

        logger.info(
            "Feed cleanup completed",
            job_id=request.job_id,
            inactive_feeds=inactive_feeds,
        )

        return FeedCleanupJobResponse(
            job_id=request.job_id,
            status="success",
            message=f"Marked {inactive_feeds} feeds inactive",
            orphaned_subscriptions=0,
            inactive_feeds=inactive_feeds,
        )


class ScheduledFeedRefreshCycleHandler(
    BaseJobHandler[
        ScheduledFeedRefreshCycleJobRequest,
        ScheduledFeedRefreshCycleJobResponse,
    ]
):
    """Handler for scheduled feed refresh cycle job.

    Refreshes all active feeds in batches as quickly as possible.
    Triggered by Arq cron on a recurring basis (every 15 minutes).
    """

    def __init__(self, _feed_application: "FeedApplication") -> None:
        """Initialize the handler.

        Args:
            _feed_application: Unused - injected feed application has its own session
                that won't commit until the HTTP request ends. We create our own
                session per feed to ensure immediate commits.

        """
        from backend.core.app import settings

        self._settings = settings

    async def execute(
        self, request: ScheduledFeedRefreshCycleJobRequest
    ) -> ScheduledFeedRefreshCycleJobResponse:
        """Execute the feed refresh cycle job.

        Queries all active feeds and refreshes them in batches as quickly
        as possible, with no artificial delays between batches.

        Each feed is processed in its own database session to ensure
        immediate commits and visibility.

        Args:
            request: The feed refresh cycle job request

        Returns:
            Response with refresh statistics

        """
        from backend.core.app import settings
        from backend.models import Feed

        start_time = time.time()
        logger.info("Starting feed refresh cycle", job_id=request.job_id)

        async with AsyncSessionLocal() as db:
            query_result = await db.execute(
                select(Feed.id)
                .where(Feed.is_active)
                .where(Feed.error_count < 3)
                .order_by(Feed.id.asc())
            )
            feed_ids = [row[0] for row in query_result.all()]

        feeds_total = len(feed_ids)
        if feeds_total == 0:
            return ScheduledFeedRefreshCycleJobResponse(
                job_id=request.job_id,
                status="success",
                message="No feeds to refresh",
                feeds_total=0,
                feeds_processed=0,
                feeds_successful=0,
                feeds_failed=0,
                new_articles_total=0,
                duration_seconds=0,
            )

        batch_size = settings.feed_refresh_batch_size

        logger.info(
            "Feed refresh cycle configured",
            job_id=request.job_id,
            feeds_total=feeds_total,
            batch_size=batch_size,
        )

        feeds_successful = 0
        feeds_failed = 0
        new_articles_total = 0

        for i in range(0, feeds_total, batch_size):
            batch = feed_ids[i : i + batch_size]

            tasks = [
                self._process_feed_with_session(feed_id) for feed_id in batch
            ]
            batch_results: list[
                BaseException | dict[str, Any]
            ] = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    feeds_failed += 1
                    logger.error("Feed refresh error", error=str(result))
                elif isinstance(result, dict):
                    if result.get("status") == "success":
                        feeds_successful += 1
                        new_articles_total += result.get("new_articles", 0)
                    elif result.get("status") == "error":
                        feeds_failed += 1
                    elif result.get("status") == "skipped":
                        feeds_successful += 1
                    else:
                        feeds_failed += 1
                        logger.warning(
                            "Unknown feed refresh result status", result=result
                        )
                else:
                    feeds_failed += 1
                    logger.error(
                        "Unexpected feed refresh result type",
                        result=type(result).__name__,
                    )

        duration_seconds = time.time() - start_time

        logger.info(
            "Feed refresh cycle completed",
            job_id=request.job_id,
            feeds_total=feeds_total,
            feeds_successful=feeds_successful,
            feeds_failed=feeds_failed,
            new_articles_total=new_articles_total,
            duration_seconds=duration_seconds,
        )

        return ScheduledFeedRefreshCycleJobResponse(
            job_id=request.job_id,
            status="success",
            message=f"Processed {feeds_total} feeds: {feeds_successful} successful, {feeds_failed} failed",
            feeds_total=feeds_total,
            feeds_processed=feeds_successful + feeds_failed,
            feeds_successful=feeds_successful,
            feeds_failed=feeds_failed,
            new_articles_total=new_articles_total,
            duration_seconds=duration_seconds,
        )

    async def _process_feed_with_session(self, feed_id: UUID) -> dict[str, Any]:
        """Process a single feed refresh with its own database session.

        Each feed gets a fresh session that commits immediately, ensuring
        articles are visible right away.

        Args:
            feed_id: The feed UUID to refresh.

        Returns:
            Dict with status, feed_id, message, and optional new_articles count.

        """
        async with AsyncSessionLocal() as db:
            try:
                from backend.infrastructure.feed.processing.feed_processor import (
                    FeedProcessor,
                )
                from backend.infrastructure.repositories import (
                    UserFeedRepository,
                )

                feed_processor = FeedProcessor(db)
                user_feed_repo = UserFeedRepository(db)

                result = await feed_processor.refresh_feed(feed_id)

                await db.commit()

                # Queue notifications for subscribed users if new articles were created
                if (
                    result.get("status") == "success"
                    and result.get("articles_created", 0) > 0
                ):
                    from backend.infrastructure.notifications.notifications import (
                        queue_new_articles_notification,
                    )

                    user_ids = (
                        await user_feed_repo.get_subscribed_user_ids_for_feed(
                            feed_id
                        )
                    )

                    for user_id in user_ids:
                        await queue_new_articles_notification(
                            user_id=user_id,
                            feed_id=feed_id,
                            article_count=result["articles_created"],
                        )

                    logger.debug(
                        "Queued notifications for feed subscribers",
                        feed_id=str(feed_id),
                        subscriber_count=len(user_ids),
                        new_articles=result["articles_created"],
                    )

                return result

            except Exception as e:
                await db.rollback()
                logger.exception(
                    "Feed refresh exception", feed_id=str(feed_id), error=str(e)
                )
                return {
                    "status": "error",
                    "feed_id": str(feed_id),
                    "message": str(e),
                }

"""Arq worker functions for background job processing.

This module contains all worker functions that will be executed by Arq.
Each function wraps an existing handler from the app/infrastructure/workers/ directory.
"""

import uuid
from typing import Any
from uuid import UUID

from structlog import get_logger

from backend.core.database import AsyncSessionLocal
from backend.infrastructure.jobs.auto_read import AutoMarkReadJobHandler
from backend.infrastructure.jobs.opml import (
    OpmlExportJobHandler,
    OpmlImportJobHandler,
)
from backend.infrastructure.jobs.scheduled import (
    FeedCleanupHandler,
    ScheduledFeedRefreshCycleHandler,
)
from backend.infrastructure.repositories import (
    SubscriptionRepository,
    UserFeedRepository,
    UserRepository,
)
from backend.schemas.workers import (
    AutoMarkReadJobRequest,
    AutoMarkReadJobResponse,
    FeedCleanupJobRequest,
    FeedCleanupJobResponse,
    OpmlExportJobRequest,
    OpmlExportJobResponse,
    OpmlImportJobRequest,
    OpmlImportJobResponse,
    ScheduledFeedRefreshCycleJobRequest,
    ScheduledFeedRefreshCycleJobResponse,
)

logger = get_logger(__name__)


async def startup(ctx: dict[str, Any]) -> None:
    """Initialize resources when Arq worker starts.

    Args:
        ctx: Arq context dictionary.

    """
    logger.info("Arq worker starting up")


async def shutdown(ctx: dict[str, Any]) -> None:
    """Clean up resources when Arq worker shuts down.

    Closes Redis and database connections. Logs errors but does not raise them.

    Args:
        ctx: Arq context dictionary.

    """
    logger.info("Arq worker initiating graceful shutdown...")

    try:
        from backend.core.database import engine

        logger.info("Closing database connections...")
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.exception("Error closing database connections", error=str(e))

    try:
        from backend.infrastructure.external.redis import close_redis

        logger.info("Closing Redis connection...")
        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.exception("Error closing Redis connection", error=str(e))

    logger.info("Arq worker shutdown completed")


async def opml_import(
    ctx: dict[str, Any],
    user_id: str,
    import_id: str,
    storage_key: str,
    filename: str,
    folder_id: str | None = None,
) -> dict[str, Any]:
    """Process OPML import job.

    Args:
        ctx: Arq context.
        user_id: User ID (UUID string).
        import_id: Import record ID (UUID string).
        storage_key: Local storage key for OPML file.
        filename: Original filename.
        folder_id: Optional folder ID for imports.

    Returns:
        Job response dict.

    """
    job_id = str(uuid.uuid4())
    logger.info(
        "Processing OPML import",
        job_id=job_id,
        user_id=user_id,
        import_id=import_id,
        filename=filename,
    )

    request = OpmlImportJobRequest(
        job_id=job_id,
        user_id=user_id,
        import_id=import_id,
        storage_key=storage_key,
        filename=filename,
        folder_id=folder_id,
    )

    handler = OpmlImportJobHandler()
    response = await handler.handle(request, job_id)

    if isinstance(response, OpmlImportJobResponse):
        return response.model_dump()
    if hasattr(response, "status_code"):
        return {
            "status": "error",
            "message": bytes(response.body).decode()
            if hasattr(response, "body")
            else str(response),
            "status_code": response.status_code,
        }
    return {"status": "error", "message": str(response)}


async def opml_export(
    ctx: dict[str, Any],
    user_id: str,
    export_id: str,
    folder_id: str | None = None,
) -> dict[str, Any]:
    """Process OPML export job.

    Args:
        ctx: Arq context.
        user_id: User ID (UUID string).
        export_id: Export record ID (UUID string).
        folder_id: Optional folder ID to filter.

    Returns:
        Job response dict.

    """
    job_id = str(uuid.uuid4())
    logger.info(
        "Processing OPML export",
        job_id=job_id,
        user_id=user_id,
        export_id=export_id,
    )

    request = OpmlExportJobRequest(
        job_id=job_id,
        user_id=user_id,
        export_id=export_id,
        folder_id=folder_id,
    )

    handler = OpmlExportJobHandler()
    response = await handler.handle(request, job_id)

    if isinstance(response, OpmlExportJobResponse):
        return response.model_dump()
    if hasattr(response, "status_code"):
        return {
            "status": "error",
            "message": bytes(response.body).decode()
            if hasattr(response, "body")
            else str(response),
            "status_code": response.status_code,
        }
    return {"status": "error", "message": str(response)}


async def feed_create_and_subscribe(
    ctx: dict[str, Any],
    url: str,
    user_id: str,
    folder_id: str | None = None,
) -> dict[str, Any]:
    """Create feed and subscribe user.

    Args:
        ctx: Arq context.
        url: Feed URL to create and subscribe to.
        user_id: User ID (UUID string).
        folder_id: Optional folder ID.

    Returns:
        Job response dict.

    """
    job_id = ctx.get("job_id", "unknown")

    logger.info(
        "Processing feed create and subscribe",
        job_id=job_id,
        url=url,
        user_id=user_id,
    )

    from backend.infrastructure.feed.processing.feed_processor import (
        FeedProcessor,
    )
    from backend.schemas.feeds import DiscoveryFeedCreateRequest

    async with AsyncSessionLocal() as db:
        try:
            user_feed_repo = UserFeedRepository(db)

            feed_processor = FeedProcessor(db)
            feed_request = DiscoveryFeedCreateRequest(url=url, title=None)
            feed = await feed_processor.create_feed(feed_request)

            subscription = await user_feed_repo.create_user_feed(
                user_id=UUID(user_id),
                feed_id=feed.id,
                title=feed.title or url,
                folder_id=UUID(folder_id) if folder_id else None,
            )

            if feed.latest_articles:
                await user_feed_repo.bulk_upsert_user_article_states(
                    UUID(user_id),
                    feed.latest_articles,
                )
                logger.info(
                    "Created user-article states for existing articles",
                    job_id=job_id,
                    feed_id=str(feed.id),
                    article_count=len(feed.latest_articles),
                )

                from backend.application.feed import FeedApplication

                feed_app = FeedApplication(db)
                tags_created = await feed_app._backfill_tags_for_articles(
                    UUID(user_id), feed.latest_articles
                )
                logger.info(
                    "Backfilled tags for new feed articles",
                    job_id=job_id,
                    feed_id=str(feed.id),
                    tags_created=tags_created,
                )

            logger.info(
                "Feed created and user subscribed",
                job_id=job_id,
                feed_id=str(feed.id),
                subscription_id=str(subscription.id),
                user_id=user_id,
            )

            result = {
                "job_id": job_id,
                "feed_id": str(feed.id),
                "subscription_id": str(subscription.id),
                "status": "completed",
            }

            await db.commit()

            from backend.infrastructure.notifications.notifications import (
                publish_notification,
            )

            await publish_notification(
                UUID(user_id),
                "discovery_subscription_success",
                {
                    "title": feed.title or url,
                    "action": "subscribed",
                    "message": "Subscribed successfully",
                },
            )

            return result

        except Exception as e:
            await db.rollback()
            from backend.infrastructure.notifications.notifications import (
                publish_notification,
            )

            await publish_notification(
                UUID(user_id),
                "discovery_subscription_failed",
                {
                    "title": url,
                    "action": "failed",
                    "message": str(e),
                },
            )
            raise


async def scheduled_feed_refresh(
    ctx: dict[str, Any],
    job_id: str | None = None,
) -> dict[str, Any]:
    """Refresh all active feeds on a schedule.

    Args:
        ctx: Arq context.
        job_id: Optional job ID.

    Returns:
        Job response dict.

    """
    if job_id is None:
        job_id = str(uuid.uuid4())

    logger.info("Processing scheduled feed refresh cycle", job_id=job_id)

    request = ScheduledFeedRefreshCycleJobRequest(job_id=job_id)

    from backend.application.feed.feed import FeedApplication

    async with AsyncSessionLocal() as db:
        try:
            feed_app = FeedApplication(db)

            handler = ScheduledFeedRefreshCycleHandler(feed_app)
            response = await handler.handle(request, job_id)

            if isinstance(response, ScheduledFeedRefreshCycleJobResponse):
                result = response.model_dump()
            elif hasattr(response, "status_code"):
                result = {
                    "status": "error",
                    "message": bytes(response.body).decode()
                    if hasattr(response, "body")
                    else str(response),
                    "status_code": response.status_code,
                }
            else:
                result = {"status": "error", "message": str(response)}
            await db.commit()
            return result

        except Exception:
            await db.rollback()
            raise


async def scheduled_feed_cleanup(
    ctx: dict[str, Any],
    job_id: str | None = None,
) -> dict[str, Any]:
    """Mark orphaned feeds inactive on a schedule.

    Args:
        ctx: Arq context.
        job_id: Optional job ID.

    Returns:
        Job response dict.

    """
    if job_id is None:
        job_id = str(uuid.uuid4())

    logger.info("Processing scheduled feed cleanup", job_id=job_id)

    request = FeedCleanupJobRequest(job_id=job_id)

    handler = FeedCleanupHandler()
    response = await handler.execute(request)

    if isinstance(response, FeedCleanupJobResponse):
        return response.model_dump()
    if hasattr(response, "status_code"):
        return {
            "status": "error",
            "message": bytes(response.body).decode()
            if hasattr(response, "body")
            else str(response),
            "status_code": response.status_code,
        }
    return {"status": "error", "message": str(response)}


async def scheduled_auto_mark_read(
    ctx: dict[str, Any],
    job_id: str | None = None,
) -> dict[str, Any]:
    """Mark old articles as read on a schedule.

    Args:
        ctx: Arq context.
        job_id: Optional job ID.

    Returns:
        Job response dict.

    """
    if job_id is None:
        job_id = str(uuid.uuid4())

    logger.info("Processing scheduled auto-mark read", job_id=job_id)

    request = AutoMarkReadJobRequest(job_id=job_id)

    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        sub_repo = SubscriptionRepository(db)

        handler = AutoMarkReadJobHandler(
            user_repository=user_repo,
            subscription_repository=sub_repo,
        )
        response = await handler.handle(request, job_id)

        if isinstance(response, AutoMarkReadJobResponse):
            return response.model_dump()
        if hasattr(response, "status_code"):
            return {
                "status": "error",
                "message": bytes(response.body).decode()
                if hasattr(response, "body")
                else str(response),
                "status_code": response.status_code,
            }
        return {"status": "error", "message": str(response)}

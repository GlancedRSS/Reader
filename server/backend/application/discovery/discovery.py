"""Discovery application that handles feed discovery and subscription."""

from typing import TYPE_CHECKING, Literal, cast
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.notifications.notifications import (
    publish_notification,
)
from backend.infrastructure.publishers import DiscoveryPublisher
from backend.infrastructure.repositories import (
    FeedRepository,
    FolderRepository,
)
from backend.infrastructure.repositories.user_feed import UserFeedRepository
from backend.models.user_feed import UserFeed
from backend.schemas.domain import FeedDiscoveryResponse

if TYPE_CHECKING:
    from backend.application.feed import FeedApplication

logger = structlog.get_logger(__name__)


class DiscoveryApplication:
    """Discovery application that handles feed discovery."""

    def __init__(
        self,
        db: AsyncSession,
        discovery_publisher: DiscoveryPublisher | None = None,
        feed_application: "FeedApplication | None" = None,
    ):
        """Initialize the discovery application."""
        self.db = db
        self.feed_repository = FeedRepository(db)
        self.user_feed_repository = UserFeedRepository(db)
        self.folder_repository = FolderRepository(db)
        self.discovery_publisher = discovery_publisher
        self.feed_application = feed_application

    async def discover_feeds(
        self, url: str, user_id: UUID, folder_id: UUID | None = None
    ) -> FeedDiscoveryResponse:
        """Discover feeds from a URL and check subscription status."""
        logger.info("Discovering feeds", url=url, user_id=str(user_id))

        existing_feed = await self.feed_repository.get_feed_by_url(url)
        if existing_feed:
            logger.info(
                "Feed already exists globally, checking subscription status",
                url=url,
                feed_id=str(existing_feed.id),
                user_id=str(user_id),
            )

            subscription = (
                await self.user_feed_repository.get_user_subscription(
                    user_id, existing_feed.id
                )
            )
            is_subscribed = subscription is not None

            if is_subscribed:
                logger.info(
                    "User already subscribed to feed",
                    url=url,
                )

                subscription = cast(UserFeed, subscription)

                action: Literal[
                    "existing", "moved", "subscribed", "pending", "failed"
                ] = "existing"
                message = "Already subscribed"
                folder_warning = None

                current_folder_id = subscription.folder_id

                if folder_id and folder_id != current_folder_id:
                    folder = await self.folder_repository.find_by_id(
                        folder_id, user_id
                    )
                    if folder:
                        await self.user_feed_repository.update_user_feed(
                            subscription, {"folder_id": folder_id}
                        )
                        action = "moved"
                        message = "Feed moved"
                    else:
                        logger.warning(
                            "Invalid folder_id provided in discover_feeds for existing subscription",
                            folder_id=str(folder_id),
                            user_id=str(user_id),
                        )
                        folder_warning = " Folder not found"
                        await publish_notification(
                            user_id,
                            "discovery_folder_not_found",
                            {
                                "title": existing_feed.title or url,
                                "action": "folder_not_found",
                                "message": folder_warning.strip(),
                            },
                        )

                if folder_warning:
                    message = f"{message}{folder_warning}"

                await publish_notification(
                    user_id,
                    "discovery_already_subscribed",
                    {
                        "title": existing_feed.title or url,
                        "action": action,
                        "message": message,
                    },
                )
                return FeedDiscoveryResponse(
                    status=action,
                    message=message,
                )

            logger.info(
                "Feed exists globally but user not subscribed, subscribing directly",
                url=url,
                user_id=str(user_id),
                folder_id=str(folder_id) if folder_id else None,
            )

            folder_warning = None
            if folder_id:
                folder = await self.folder_repository.find_by_id(
                    folder_id, user_id
                )
                if not folder:
                    logger.warning(
                        "Invalid folder_id provided in discover_feeds, adding feed at root",
                        folder_id=str(folder_id),
                        user_id=str(user_id),
                    )
                    folder_id = None
                    folder_warning = " Folder not found, added to root"
                    await publish_notification(
                        user_id,
                        "discovery_folder_not_found",
                        {
                            "title": url,
                            "action": "folder_not_found",
                            "message": folder_warning.strip(),
                        },
                    )

            try:
                subscription = await self.user_feed_repository.create_user_feed(
                    user_id=user_id,
                    feed_id=existing_feed.id,
                    title=existing_feed.title or url,
                    folder_id=folder_id,
                )

                if existing_feed.latest_articles:
                    await self.user_feed_repository.bulk_upsert_user_article_states(
                        user_id,
                        existing_feed.latest_articles,
                    )
                    logger.info(
                        "Created user-article states for existing feed articles",
                        feed_id=str(existing_feed.id),
                        article_count=len(existing_feed.latest_articles),
                    )

                    if self.feed_application:
                        tags_created = await self.feed_application._backfill_tags_for_articles(
                            user_id, existing_feed.latest_articles
                        )
                        logger.info(
                            "Backfilled tags for existing feed articles",
                            feed_id=str(existing_feed.id),
                            tags_created=tags_created,
                        )

                action = "subscribed"
                logger.info(
                    "Subscription created successfully",
                    user_id=str(user_id),
                    subscription_id=str(subscription.id),
                    action=action,
                )
                feed_title = existing_feed.title or url
                message = "Subscribed successfully"
                if folder_warning:
                    message = f"{message}. {folder_warning.strip()}"
                await publish_notification(
                    user_id,
                    "discovery_subscription_success",
                    {
                        "title": feed_title,
                        "action": action,
                        "message": message,
                    },
                )
                return FeedDiscoveryResponse(
                    status="subscribed",
                    message=message,
                )
            except Exception as e:
                error_message = str(e)
                logger.exception(
                    "Failed to create subscription",
                    error=error_message,
                    error_type=type(e).__name__,
                    url=url,
                )
                await publish_notification(
                    user_id,
                    "discovery_subscription_failed",
                    {
                        "title": url,
                        "action": "failed",
                        "message": error_message,
                    },
                )
                return FeedDiscoveryResponse(
                    status="failed",
                    message=error_message,
                )

        logger.info(
            "Feed doesn't exist globally, queuing create and subscribe job",
            url=url,
            user_id=str(user_id),
            folder_id=str(folder_id) if folder_id else None,
        )

        if folder_id:
            folder = await self.folder_repository.find_by_id(folder_id, user_id)
            if not folder:
                logger.warning(
                    "Invalid folder_id provided in discover_feeds (worker job), adding feed at root",
                    folder_id=str(folder_id),
                    user_id=str(user_id),
                )
                folder_id = None
                await publish_notification(
                    user_id,
                    "discovery_folder_not_found",
                    {
                        "title": url,
                        "action": "folder_not_found",
                        "message": "Folder not found, added to root",
                    },
                )

        if not self.discovery_publisher:
            error_message = "Service unavailable"
            logger.error(
                "DiscoveryPublisher not configured - cannot queue new feed job",
                url=url,
                user_id=str(user_id),
            )
            await publish_notification(
                user_id,
                "discovery_subscription_failed",
                {
                    "title": url,
                    "action": "failed",
                    "message": error_message,
                },
            )
            return FeedDiscoveryResponse(
                status="failed",
                message=error_message,
            )

        try:
            result = await self.discovery_publisher.publish_create_and_subscribe_with_job(
                url=url,
                user_id=user_id,
                folder_id=folder_id,
            )
            logger.info(
                "Worker job published successfully",
                job_id=result.get("job_id"),
                message_id=result.get("message_id"),
                url=url,
                user_id=str(user_id),
            )
            return FeedDiscoveryResponse(
                status="pending",
                message="Adding feed...",
            )
        except Exception as e:
            error_message = str(e)
            logger.exception(
                "Failed to publish worker job",
                error=error_message,
                error_type=type(e).__name__,
                url=url,
            )
            await publish_notification(
                user_id,
                "discovery_subscription_failed",
                {
                    "title": url,
                    "action": "failed",
                    "message": error_message,
                },
            )
            return FeedDiscoveryResponse(
                status="failed",
                message=error_message,
            )

"""Feed repository for database operations."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Feed
from backend.utils.url_normalizer import normalize_url

logger = structlog.get_logger()


class FeedRepository:
    """Repository for feed database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the feed repository."""
        self.db = db

    async def get_feed_by_id(self, feed_id: UUID) -> Feed | None:
        """Get feed by ID."""
        return await self.db.get(Feed, feed_id)

    async def get_feed_by_url(self, url: str) -> Feed | None:
        """Get feed by URL."""
        normalized_url = normalize_url(url)
        stmt = select(Feed).where(Feed.canonical_url == normalized_url)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_feed(
        self,
        url: str,
        title: str,
        description: str | None,
        feed_type: str,
        language: str | None,
        website: str | None,
        has_articles: bool,
    ) -> Feed:
        """Create a new feed in the database."""
        canonical_url = normalize_url(url) if url else None

        feed_record = Feed(
            canonical_url=canonical_url,
            title=title,
            description=description,
            feed_type=feed_type,
            language=language,
            website=website,
            last_fetched_at=datetime.now(UTC) if has_articles else None,
        )

        self.db.add(feed_record)
        await self.db.flush()

        return feed_record

    async def delete_feed(self, feed: Feed) -> None:
        """Delete a feed record."""
        await self.db.delete(feed)

    async def update_feed(
        self, feed_id: UUID, feed_data: dict[str, Any]
    ) -> Feed | None:
        """Update feed with provided data."""
        result = await self.db.execute(select(Feed).where(Feed.id == feed_id))
        feed = result.scalar_one_or_none()

        if not feed:
            return None

        for field, value in feed_data.items():
            setattr(feed, field, value)

        await self.db.flush()
        await self.db.refresh(feed)
        logger.info(
            "Updated feed",
            feed_id=feed_id,
            updated_fields=list(feed_data.keys()),
        )
        return feed

    async def delete_feeds_bulk(self, feed_ids: list[UUID]) -> int:
        """Delete multiple feeds in a single query."""
        if not feed_ids:
            return 0

        result = await self.db.execute(
            delete(Feed).where(Feed.id.in_(feed_ids))
        )
        await self.db.flush()

        count = result.rowcount
        logger.info("Bulk deleted feeds", count=count, feed_ids=len(feed_ids))
        return count

    async def update_feed_stats(
        self,
        feed_id: UUID,
        last_fetched_at: datetime | None = None,
        last_update: datetime | None = None,
        error_count: int | None = None,
        last_error: str | None = None,
    ) -> None:
        """Update feed statistics after a fetch attempt."""
        result = await self.db.execute(select(Feed).where(Feed.id == feed_id))
        feed = result.scalar_one_or_none()

        if feed:
            if last_fetched_at is not None:
                feed.last_fetched_at = last_fetched_at
            if last_update is not None:
                feed.last_update = last_update
            if error_count is not None:
                feed.error_count = error_count
            if last_error is not None:
                feed.last_error = last_error
                feed.last_error_at = datetime.now(UTC)

    async def increment_feed_error(
        self,
        feed_id: UUID,
        error_message: str,
    ) -> None:
        """Increment feed error count."""
        result = await self.db.execute(select(Feed).where(Feed.id == feed_id))
        feed = result.scalar_one_or_none()

        if feed:
            feed.error_count = feed.error_count + 1
            feed.last_error = error_message
            feed.last_error_at = datetime.now(UTC)

    async def reset_feed_errors(self, feed_id: UUID) -> None:
        """Reset error count for a successful fetch."""
        result = await self.db.execute(select(Feed).where(Feed.id == feed_id))
        feed = result.scalar_one_or_none()

        if feed:
            feed.error_count = 0
            feed.last_error = None
            feed.last_error_at = None

    async def get_active_feeds_with_subscriptions(self) -> list[Feed]:
        """Get all active feeds that have user subscriptions."""
        from backend.models import ArticleSource, UserArticle

        stmt = (
            select(Feed)
            .join(ArticleSource, Feed.id == ArticleSource.feed_id)
            .join(
                UserArticle, ArticleSource.article_id == UserArticle.article_id
            )
            .where(Feed.is_active)
            .distinct()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def bulk_mark_orphaned_feeds_inactive(self) -> int:
        """Mark all feeds with no subscribers as inactive in a single query."""
        query = text("""
            UPDATE content.feeds
            SET is_active = false
            WHERE is_active = true
              AND id NOT IN (
                  SELECT DISTINCT feed_id
                  FROM content.user_feeds
              )
            RETURNING COUNT(*) as feeds_marked_inactive
        """)

        result = await self.db.execute(query)
        count = result.scalar() or 0

        await self.db.commit()

        logger.info("Bulk marked orphaned feeds inactive", count=count)
        return count

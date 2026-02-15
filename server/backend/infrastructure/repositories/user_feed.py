"""Repository for user feed (subscription) data access operations and queries."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast
from uuid import UUID

import structlog
from sqlalchemy import and_, case, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import (
    ArticleSource,
    Feed,
    UserArticle,
    UserFeed,
    UserFolder,
    UserPreferences,
)
from backend.utils.cursor import (
    create_feed_cursor_data,
    encode_cursor_data,
)

logger = structlog.get_logger()


@dataclass
class UserFeedsQueryResult:
    """Result from cursor-based paginated user feeds query."""

    user_feeds: Sequence[UserFeed]
    next_cursor: str | None
    has_more: bool


class UserFeedRepository:
    """Repository for user feed and article-tag relationship data access."""

    def __init__(self, db: AsyncSession):
        """Initialize the user feed repository.

        Args:
            db: Async database session.

        """
        self.db = db

    async def _get_sort_order(self, user_id: UUID) -> tuple[Any, bool]:
        """Get sort order for feeds based on user preferences.

        Returns:
            Tuple of (secondary_sort, is_alphabetical)

        """
        prefs_query = select(UserPreferences).where(
            UserPreferences.user_id == user_id
        )
        prefs_result = await self.db.execute(prefs_query)
        user_prefs = prefs_result.scalar_one_or_none()

        feed_sort_order = (
            user_prefs.feed_sort_order if user_prefs else "recent_first"
        )

        if feed_sort_order == "alphabetical":
            return UserFeed.title.asc(), True
        return Feed.last_update.desc().nullslast(), False

    async def get_user_feeds_paginated(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
        order_by: str | None = None,
        folder_id: UUID | None = None,
        all: bool = False,
    ) -> Sequence[UserFeed]:
        """Get user's feed subscriptions with pagination and optional folder filtering.

        Args:
            user_id: The user ID to fetch feeds for.
            limit: Maximum number of feeds to return.
            offset: Number of feeds to skip.
            order_by: Optional sort order override.
            folder_id: Optional folder ID to filter by (None = feeds without folder).
            all: Return all feeds regardless of folder assignment.

        Returns:
            Sequence of UserFeed objects.

        """
        base_conditions = [UserFeed.user_id == user_id]

        if not all:
            if folder_id is None:
                base_conditions.append(UserFeed.folder_id.is_(None))
            else:
                base_conditions.append(UserFeed.folder_id == folder_id)

        secondary_sort: Any
        if order_by is not None:
            if order_by == "name_asc":
                secondary_sort = UserFeed.title.asc()
            elif order_by == "name_desc":
                secondary_sort = UserFeed.title.desc()
            elif order_by == "latest_article_asc":
                secondary_sort = Feed.last_update.asc().nullsfirst()
            elif order_by == "latest_article_desc":
                secondary_sort = Feed.last_update.desc().nullslast()
            else:
                secondary_sort = Feed.last_update.desc().nullslast()
        else:
            secondary_sort, _ = await self._get_sort_order(user_id)

        order_clause = (
            case(
                (UserFeed.is_pinned, 0),
                (UserFeed.is_pinned.is_(False), 1),
            ).asc(),
            secondary_sort,
        )

        stmt = (
            select(UserFeed)
            .options(selectinload(UserFeed.feed))
            .join(Feed, UserFeed.feed_id == Feed.id)
            .where(and_(*base_conditions))
            .order_by(*order_clause)
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user_feeds_paginated_cursor(
        self,
        user_id: UUID,
        limit: int,
        cursor_data: dict[str, Any] | None,
        folder_id: UUID | None = None,
        all: bool = False,
    ) -> UserFeedsQueryResult:
        """Get user's feed subscriptions with cursor-based pagination (recent ordering).

        Args:
            user_id: The user ID to fetch feeds for.
            limit: Maximum number of feeds to return.
            cursor_data: Parsed cursor data with last_update and user_feed_id.
            folder_id: Optional folder ID to filter by (None = feeds without folder).
            all: Return all feeds regardless of folder assignment.

        Returns:
            UserFeedsQueryResult containing user feeds and pagination metadata.

        """
        base_conditions = [UserFeed.user_id == user_id]

        if not all:
            if folder_id is None:
                base_conditions.append(UserFeed.folder_id.is_(None))
            else:
                base_conditions.append(UserFeed.folder_id == folder_id)

        order_clause = (
            case(
                (UserFeed.is_pinned, 0),
                (UserFeed.is_pinned.is_(False), 1),
            ).asc(),
            Feed.last_update.desc().nullslast(),
            UserFeed.id.desc(),
        )

        stmt = (
            select(UserFeed)
            .options(selectinload(UserFeed.feed))
            .join(Feed, UserFeed.feed_id == Feed.id)
            .where(and_(*base_conditions))
        )

        if cursor_data:
            last_update = cursor_data.get("last_update")
            user_feed_id = cursor_data.get("user_feed_id")

            if last_update:
                cursor_updated_at = datetime.fromisoformat(
                    last_update.replace("Z", "+00:00")
                )
            else:
                cursor_updated_at = None

            if user_feed_id:
                feed_id = UUID(user_feed_id)
            else:
                feed_id = None

            if cursor_updated_at is not None:
                if feed_id:
                    stmt = stmt.where(
                        or_(
                            UserFeed.is_pinned.is_(True),
                            Feed.last_update < cursor_updated_at,
                            and_(
                                Feed.last_update == cursor_updated_at,
                                UserFeed.id < feed_id,
                            ),
                        )
                    )
                else:
                    stmt = stmt.where(
                        or_(
                            UserFeed.is_pinned.is_(True),
                            Feed.last_update < cursor_updated_at,
                        )
                    )
            elif feed_id:
                stmt = stmt.where(
                    or_(
                        UserFeed.is_pinned.is_(True),
                        UserFeed.id < feed_id,
                    )
                )

        stmt = stmt.order_by(*order_clause).limit(limit + 1)

        result = await self.db.execute(stmt)
        user_feeds = result.scalars().all()

        has_more = len(user_feeds) > limit
        if has_more:
            user_feeds = user_feeds[:-1]

        next_cursor = None
        if user_feeds and has_more:
            last_feed = user_feeds[-1]
            last_updated_at = (
                last_feed.feed.last_update if last_feed.feed else None
            )
            cursor_dict = create_feed_cursor_data(last_feed.id, last_updated_at)
            next_cursor = encode_cursor_data(cursor_dict)

        return UserFeedsQueryResult(
            user_feeds=user_feeds,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_user_subscription(
        self, user_id: UUID, feed_id: UUID
    ) -> UserFeed | None:
        """Get user's subscription to a specific feed.

        Args:
            user_id: The user ID.
            feed_id: The feed ID.

        Returns:
            The UserFeed if found, None otherwise.

        """
        stmt = select(UserFeed).where(
            and_(
                UserFeed.user_id == user_id,
                UserFeed.feed_id == feed_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_feed_by_id(self, user_feed_id: UUID) -> UserFeed | None:
        """Get user feed by ID with eager loaded feed and folder.

        Args:
            user_feed_id: The user feed ID.

        Returns:
            The UserFeed with feed and folder loaded, or None if not found.

        """
        from sqlalchemy.orm import selectinload

        result = await self.db.execute(
            select(UserFeed)
            .options(
                selectinload(UserFeed.feed),
                selectinload(UserFeed.folder),
            )
            .where(UserFeed.id == user_feed_id)
        )
        return result.scalar_one_or_none()

    async def find_by_id(
        self, user_feed_id: UUID, user_id: UUID
    ) -> UserFeed | None:
        """Get user feed by ID with user filtering.

        Args:
            user_feed_id: The user feed ID.
            user_id: The user ID.

        Returns:
            The UserFeed if found and belongs to user, None otherwise.

        """
        stmt = select(UserFeed).where(
            and_(
                UserFeed.id == user_feed_id,
                UserFeed.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def validate_folder_for_user(
        self, user_id: UUID, folder_id: UUID
    ) -> UserFolder | None:
        """Validate that a folder exists and belongs to the user.

        Args:
            user_id: The user ID
            folder_id: The folder ID to validate

        Returns:
            The UserFolder if valid, None otherwise

        """
        stmt = select(UserFolder).where(
            and_(
                UserFolder.id == folder_id,
                UserFolder.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_feeds_count(
        self, user_id: UUID, folder_id: UUID | None = None, all: bool = False
    ) -> int:
        """Get total count of user's feed subscriptions with optional folder filtering.

        Args:
            user_id: The user ID
            folder_id: Optional folder ID to filter by (None = feeds without folder)
            all: Return all feeds regardless of folder assignment

        Returns:
            Total count of user feeds matching the criteria

        """
        base_conditions = [UserFeed.user_id == user_id]

        if not all:
            if folder_id is None:
                base_conditions.append(UserFeed.folder_id.is_(None))
            else:
                base_conditions.append(UserFeed.folder_id == folder_id)

        count_query = select(func.count(UserFeed.id)).where(
            and_(*base_conditions)
        )
        result = await self.db.execute(count_query)
        return result.scalar() or 0

    async def create_user_feed(
        self,
        user_id: UUID,
        feed_id: UUID,
        title: str,
        folder_id: UUID | None = None,
    ) -> UserFeed:
        """Create a new user feed subscription.

        Args:
            user_id: The user ID.
            feed_id: The feed ID to subscribe to.
            title: The title for the user feed.
            folder_id: Optional folder ID to place the user feed in.

        Returns:
            The created UserFeed.

        """
        user_feed = UserFeed(
            user_id=user_id,
            feed_id=feed_id,
            title=title,
            folder_id=folder_id,
        )

        self.db.add(user_feed)
        await self.db.flush()
        await self.db.refresh(user_feed)

        return user_feed

    async def update_user_feed(
        self, user_feed: UserFeed, update_data: dict[str, Any]
    ) -> UserFeed:
        """Update a user feed with the provided data.

        Args:
            user_feed: The UserFeed to update.
            update_data: Dictionary of fields to update.

        Returns:
            The updated UserFeed.

        """
        for field, value in update_data.items():
            if hasattr(user_feed, field):
                setattr(user_feed, field, value)

        await self.db.flush()
        await self.db.refresh(user_feed)

        return user_feed

    async def delete_user_feed(self, user_feed: UserFeed) -> None:
        """Delete a user feed.

        Args:
            user_feed: The UserFeed to delete.

        """
        await self.db.delete(user_feed)

    async def get_recent_article_ids_for_feed(
        self, feed_id: UUID, since_timestamp: datetime
    ) -> list[UUID]:
        """Get article IDs from a feed's latest_articles array.

        The latest_articles array contains article IDs from the most recent
        feed fetch. This ensures users only see articles that were recently
        added to the system, regardless of their published_at date.

        Args:
            feed_id: The feed ID to get article IDs for.
            since_timestamp: User feed timestamp (kept for logging context,
                but not used for filtering since we use latest_articles).

        Returns:
            List of article UUIDs from the feed's latest_articles.

        """
        logger.info(
            "Getting recent article IDs for feed",
            feed_id=str(feed_id),
            since_timestamp=since_timestamp.isoformat(),
        )

        feed_query = select(Feed.latest_articles).where(Feed.id == feed_id)
        feed_result = await self.db.execute(feed_query)
        latest_articles = feed_result.scalar_one_or_none()

        if latest_articles:
            result = latest_articles
        else:
            result = []

        logger.info(
            "Latest articles from feed",
            feed_id=str(feed_id),
            article_count=len(result),
        )

        return result

    async def bulk_upsert_user_article_states(
        self, user_id: UUID, article_ids: list[UUID]
    ) -> int:
        """Bulk insert UserArticle records with conflict handling.

        Args:
            user_id: The user ID.
            article_ids: List of article IDs to create states for.

        Returns:
            Number of records created.

        """
        if not article_ids:
            return 0

        values_list = []
        params = {"user_id": str(user_id)}
        for i, article_id in enumerate(article_ids):
            values_list.append(f"(:user_id, :article_id_{i}, false, false)")
            params[f"article_id_{i}"] = str(article_id)

        query = text(
            f"""
            INSERT INTO content.user_articles (user_id, article_id, is_read, read_later)
            VALUES {",".join(values_list)}
            ON CONFLICT (user_id, article_id)
            DO NOTHING
            """
        )
        result = await self.db.execute(query, params)
        return result.rowcount if hasattr(result, "rowcount") else 0

    async def recalculate_user_feed_unread_count(
        self, user_feed_id: UUID
    ) -> int | None:
        """Call stored procedure to recalculate user feed unread count.

        Args:
            user_feed_id: The user feed ID to recalculate.

        Returns:
            The recalculated count, or None if the call fails.

        """
        try:
            recalc_result = await self.db.execute(
                text(
                    "SELECT content.recalculate_subscription_unread_count(:subscription_id)"
                ),
                {"subscription_id": user_feed_id},
            )
            return recalc_result.scalar()
        except Exception as e:
            logger.warning(
                "Could not calculate initial unread count for user feed",
                user_feed_id=user_feed_id,
                error=str(e),
            )
            return None

    async def get_article_ids_for_feed(self, feed_id: UUID) -> list[UUID]:
        """Get all article IDs for a feed via article_sources junction table.

        Args:
            feed_id: The feed ID.

        Returns:
            List of article IDs linked to this feed.

        """
        stmt = select(ArticleSource.article_id).where(
            ArticleSource.feed_id == feed_id
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_article_ids_for_feeds(
        self, feed_ids: list[UUID]
    ) -> list[UUID]:
        """Get all article IDs for multiple feeds via article_sources junction table.

        Args:
            feed_ids: List of feed IDs.

        Returns:
            List of unique article IDs linked to these feeds.

        """
        if not feed_ids:
            return []

        stmt = select(ArticleSource.article_id).where(
            ArticleSource.feed_id.in_(feed_ids)
        )
        result = await self.db.execute(stmt)
        return list({row[0] for row in result.all()})

    async def delete_user_articles(
        self, user_id: UUID, article_ids: list[UUID]
    ) -> int:
        """Delete UserArticle records for specific articles.

        Args:
            user_id: The user ID.
            article_ids: List of article IDs to delete.

        Returns:
            Number of records deleted.

        """
        if not article_ids:
            return 0

        from sqlalchemy import delete

        delete_stmt = delete(UserArticle).where(
            and_(
                UserArticle.user_id == user_id,
                UserArticle.article_id.in_(article_ids),
            )
        )
        result = await self.db.execute(delete_stmt)
        return cast(Any, result).rowcount or 0

    async def get_subscribed_user_ids_for_feed(
        self, feed_id: UUID
    ) -> list[UUID]:
        """Get all user IDs subscribed to a feed.

        Args:
            feed_id: The feed ID.

        Returns:
            List of user IDs with active subscriptions to this feed.

        """
        stmt = select(UserFeed.user_id).where(
            and_(
                UserFeed.feed_id == feed_id,
                UserFeed.is_active.is_(True),
            )
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_article_ids_accessible_via_other_feeds(
        self,
        user_id: UUID,
        article_ids: list[UUID],
        exclude_feed_ids: list[UUID],
    ) -> set[UUID]:
        """Get article IDs that are accessible via other user subscriptions.

        Bulk query that checks all articles at once instead of looping.

        Args:
            user_id: The user ID.
            article_ids: List of article IDs to check.
            exclude_feed_ids: Feed IDs to exclude (feeds being unsubscribed/rolled back).

        Returns:
            Set of article IDs that are accessible via other feeds.

        """
        if not article_ids:
            return set()

        stmt = select(
            ArticleSource.article_id,
            ArticleSource.feed_id,
        ).where(
            and_(
                ArticleSource.article_id.in_(article_ids),
                ArticleSource.feed_id.notin_(exclude_feed_ids),
            )
        )
        result = await self.db.execute(stmt)
        article_feed_pairs = result.all()

        if not article_feed_pairs:
            return set()

        other_feed_ids = list({feed_id for _, feed_id in article_feed_pairs})

        feed_stmt = select(UserFeed.feed_id).where(
            and_(
                UserFeed.user_id == user_id,
                UserFeed.feed_id.in_(other_feed_ids),
                UserFeed.is_active.is_(True),
            )
        )
        result = await self.db.execute(feed_stmt)
        subscribed_feed_ids = {row[0] for row in result.all()}

        return {
            article_id
            for article_id, feed_id in article_feed_pairs
            if feed_id in subscribed_feed_ids
        }

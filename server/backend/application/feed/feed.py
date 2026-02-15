"""Application service for feed subscription operations."""

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundError, ValidationError
from backend.domain import (
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
)
from backend.domain.feed.feed import FeedDomain
from backend.infrastructure.notifications.notifications import (
    publish_notification,
)
from backend.infrastructure.repositories import FeedRepository
from backend.infrastructure.repositories.tag import UserTagRepository
from backend.infrastructure.repositories.user_feed import UserFeedRepository
from backend.schemas.core import (
    PaginatedResponse,
    PaginationMetadata,
    ResponseMessage,
)
from backend.schemas.domain import (
    UserFeedListResponse,
    UserFeedResponse,
    UserFeedUpdateRequest,
)
from backend.utils.cursor import parse_cursor_data

logger = structlog.get_logger()


class FeedApplication:
    """Application service for feed subscription operations."""

    def __init__(
        self,
        db: AsyncSession,
    ):
        """Initialize the feed application with database session and services.

        Args:
            db: Async database session for repository operations.

        """
        self.db = db
        self.repository = UserFeedRepository(db)
        self.feed_repository = FeedRepository(db)
        self.tag_repository = UserTagRepository(db)
        self.feed_domain = FeedDomain()

    async def get_user_feeds_paginated(
        self,
        user_id: UUID,
        folder_id: UUID | None = None,
        order_by: str | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        cursor: str | None = None,
        all: bool = False,
    ) -> PaginatedResponse[UserFeedListResponse]:
        """Get user's subscriptions with filtering and pagination.

        Args:
            user_id: The ID of the user.
            folder_id: Optional filter by folder ID.
            order_by: Order by 'name' (alphabetical A-Z, offset-based) or 'recent' (cursor-based).
            limit: Maximum number of subscriptions to return.
            offset: Number of subscriptions to skip (used for name ordering).
            cursor: Pagination cursor (used for recent ordering).
            all: Return all feeds regardless of folder assignment. When true, folder_id is ignored.

        Returns:
            Paginated response containing user's subscriptions.

        """
        result = []
        total = 0
        has_more = False
        next_cursor = None

        is_cursor_based = order_by == "recent"

        if is_cursor_based:
            cursor_data = parse_cursor_data(cursor)
            query_result = (
                await self.repository.get_user_feeds_paginated_cursor(
                    user_id,
                    limit=limit,
                    cursor_data=cursor_data,
                    folder_id=folder_id,
                    all=all,
                )
            )
            subscriptions = query_result.user_feeds
            has_more = query_result.has_more
            next_cursor = query_result.next_cursor
            total = await self.repository.get_user_feeds_count(
                user_id, folder_id, all
            )
        else:
            subscriptions = await self.repository.get_user_feeds_paginated(
                user_id,
                limit=limit,
                offset=offset,
                order_by="name_asc" if order_by == "name" else None,
                folder_id=folder_id,
                all=all,
            )
            total = await self.repository.get_user_feeds_count(
                user_id, folder_id, all
            )
            has_more = offset + limit < total

        for subscription in subscriptions:
            website = subscription.feed.website if subscription.feed else None
            status = self.feed_domain.calculate_feed_status(subscription.feed)
            unread_count = subscription.unread_count or 0

            sub_response = UserFeedListResponse(
                id=subscription.id,
                title=subscription.title,
                unread_count=unread_count,
                status=status,
                website=website,
                is_pinned=subscription.is_pinned or False,
                is_active=(
                    subscription.is_active
                    if subscription.is_active is not None
                    else True
                ),
            )
            result.append(sub_response)

        if order_by == "name":
            result.sort(key=lambda x: x.title.lower() if x.title else "")
            if offset:
                result = result[offset:]
            if limit:
                result = result[:limit]
                has_more = offset + limit < total

        pagination = PaginationMetadata(
            total=total,
            limit=limit,
            offset=offset if not is_cursor_based else 0,
            has_more=has_more,
            next_cursor=next_cursor,
        )

        return PaginatedResponse(data=result, pagination=pagination)

    async def get_user_feed_by_id(
        self, user_feed_id: UUID, user_id: UUID
    ) -> UserFeedResponse:
        """Get detailed user feed information by ID.

        Args:
            user_feed_id: The ID of the user feed.
            user_id: The ID of the user.

        Returns:
            Detailed user feed response.

        Raises:
            NotFoundError: If user feed is not found or feed not found.

        """
        user_feed = await self.repository.get_user_feed_by_id(user_feed_id)

        if not user_feed or user_feed.user_id != user_id:
            raise NotFoundError("Feed not found")

        feed = user_feed.feed
        if not feed:
            raise NotFoundError("Feed not found")

        status = self.feed_domain.calculate_feed_status(feed)
        unread_count = user_feed.unread_count or 0

        return UserFeedResponse(
            title=user_feed.title,
            description=feed.description,
            unread_count=unread_count,
            status=status,
            website=feed.website or "",
            is_pinned=user_feed.is_pinned or False,
            folder_id=user_feed.folder_id,
            folder_name=user_feed.folder.name if user_feed.folder else None,
            language=feed.language,
            last_update=feed.last_update,
            is_active=(
                user_feed.is_active if user_feed.is_active is not None else True
            ),
            canonical_url=feed.canonical_url,
        )

    async def update_user_feed(
        self,
        user_feed_id: UUID,
        user_feed_data: UserFeedUpdateRequest,
        user_id: UUID,
    ) -> ResponseMessage:
        """Update user's feed by user feed ID.

        Args:
            user_feed_id: The ID of the user feed to update.
            user_feed_data: The user feed update request.
            user_id: The ID of the user.

        Returns:
            Response message indicating successful update.

        Raises:
            ValueError: If user feed not found or folder invalid.

        """
        user_feed = await self.repository.get_user_feed_by_id(user_feed_id)

        if not user_feed or user_feed.user_id != user_id:
            raise NotFoundError("Feed not found")

        provided_data = user_feed_data.model_dump(exclude_unset=True)
        update_data = {}

        if "title" in provided_data:
            update_data["title"] = provided_data["title"]

        if "is_pinned" in provided_data:
            update_data["is_pinned"] = provided_data["is_pinned"]

        if "folder_id" in provided_data:
            folder_id_value = provided_data["folder_id"]

            if folder_id_value:
                folder = await self.repository.validate_folder_for_user(
                    user_id, folder_id_value
                )

                if not folder:
                    raise ValidationError("Invalid folder ID")

            update_data["folder_id"] = folder_id_value

        is_resuming = False
        if "is_active" in provided_data:
            new_is_active = provided_data["is_active"]
            if new_is_active and not user_feed.is_active:
                is_resuming = True
            update_data["is_active"] = new_is_active

        if update_data:
            await self.repository.update_user_feed(user_feed, update_data)

        if is_resuming:
            backfill_failed = False
            try:
                now = datetime.now(UTC)
                recent_article_ids = (
                    await self.repository.get_recent_article_ids_for_feed(
                        user_feed.feed_id,
                        now,
                    )
                )

                if recent_article_ids:
                    records_created = (
                        await self.repository.bulk_upsert_user_article_states(
                            user_id, recent_article_ids
                        )
                    )

                    logger.info(
                        "Created user_article_states for recent articles on resume",
                        user_id=user_id,
                        user_feed_id=user_feed_id,
                        feed_id=user_feed.feed_id,
                        article_count=len(recent_article_ids),
                        records_created=records_created,
                    )

                    tags_created = await self._backfill_tags_for_articles(
                        user_id, recent_article_ids
                    )

                    logger.info(
                        "Backfilled tags for resumed user feed",
                        user_id=user_id,
                        user_feed_id=user_feed_id,
                        feed_id=user_feed.feed_id,
                        tags_created=tags_created,
                    )

                else:
                    logger.info(
                        "No recent articles found for resumed user feed",
                        user_id=user_id,
                        user_feed_id=user_feed_id,
                        feed_id=user_feed.feed_id,
                    )

            except Exception as resume_error:
                backfill_failed = True
                logger.exception(
                    "Error creating user_article_states on resume",
                    user_id=user_id,
                    user_feed_id=user_feed_id,
                    feed_id=user_feed.feed_id,
                    error=str(resume_error),
                )
                await publish_notification(
                    user_id,
                    "feed_resume_backfill_failed",
                    {
                        "feed_id": str(user_feed.feed_id),
                        "user_feed_id": str(user_feed_id),
                        "error": "Article backfill failed after resume. The feed is active, but recent articles may not appear.",
                    },
                )

        if is_resuming and backfill_failed:
            return ResponseMessage(
                message="User feed resumed, but some articles may not appear immediately"
            )
        return ResponseMessage(message="User feed updated successfully")

    async def unsubscribe_from_feed(
        self, user_feed_id: UUID, user_id: UUID
    ) -> ResponseMessage:
        """Unsubscribe from feed.

        Deletes UserFeed and UserArticles that are not accessible via other
            user subscriptions.

        Args:
            user_feed_id: The ID of the user feed to cancel.
            user_id: The ID of the user.

        Returns:
            Response message indicating successful unsubscription.

        Raises:
            NotFoundError: If user feed is not found.

        """
        user_feed = await self.repository.get_user_feed_by_id(user_feed_id)

        if not user_feed or user_feed.user_id != user_id:
            raise NotFoundError("Feed not found")

        feed_id = user_feed.feed_id

        article_ids = await self.repository.get_article_ids_for_feed(feed_id)

        accessible_article_ids = (
            await self.repository.get_article_ids_accessible_via_other_feeds(
                user_id, article_ids, [feed_id]
            )
        )

        articles_to_delete = [
            aid for aid in article_ids if aid not in accessible_article_ids
        ]

        if articles_to_delete:
            await self.tag_repository.remove_articles_from_all_tags(
                articles_to_delete, user_id
            )

            deleted_count = await self.repository.delete_user_articles(
                user_id, articles_to_delete
            )

            logger.info(
                "Deleted user articles for feed (orphaned articles only)",
                user_id=str(user_id),
                user_feed_id=str(user_feed_id),
                total_articles=len(article_ids),
                deleted_count=deleted_count,
                kept_count=len(article_ids) - deleted_count,
            )
        else:
            logger.info(
                "All articles accessible via other feeds, none deleted",
                user_id=str(user_id),
                user_feed_id=str(user_feed_id),
                total_articles=len(article_ids),
            )

        await self.repository.delete_user_feed(user_feed)

        logger.info(
            "Successfully unsubscribed from feed",
            user_id=str(user_id),
            user_feed_id=str(user_feed_id),
            feed_id=str(feed_id),
        )

        return ResponseMessage(message="Successfully unsubscribed")

    async def _backfill_tags_for_articles(
        self, user_id: UUID, article_ids: list[UUID]
    ) -> int:
        """Backfill tags for a user from specific articles.

        Creates UserTag and ArticleTag records for existing articles based on
        their source_tags field.

        Args:
            user_id: The user ID to backfill tags for.
            article_ids: List of article IDs to backfill tags for.

        Returns:
            Number of ArticleTag records created.

        """
        if not article_ids:
            return 0

        from sqlalchemy import select

        from backend.models import Article, ArticleTag, UserArticle

        articles_query = select(Article).where(Article.id.in_(article_ids))
        result = await self.db.execute(articles_query)
        articles = result.scalars().all()

        user_articles_query = select(UserArticle).where(
            (UserArticle.user_id == user_id)
            & (UserArticle.article_id.in_(article_ids))
        )
        user_articles_result = await self.db.execute(user_articles_query)
        user_articles = user_articles_result.scalars().all()

        article_to_user_article = {ua.article_id: ua.id for ua in user_articles}

        unique_tag_names = set()
        article_tag_pairs = []
        for article in articles:
            source_tags = article.source_tags or []
            for tag_name in source_tags:
                unique_tag_names.add(tag_name)
                article_tag_pairs.append((article.id, tag_name))

        if not unique_tag_names or not article_to_user_article:
            return 0

        tag_name_to_id: dict[str, UUID] = {}
        for tag_name in unique_tag_names:
            tag = await self.tag_repository.get_or_create_tag(
                user_id=user_id,
                name=tag_name,
            )
            tag_name_to_id[tag_name] = tag.id

        user_article_ids = list(article_to_user_article.values())
        existing_pairs_query = select(
            ArticleTag.user_article_id, ArticleTag.user_tag_id
        ).where(
            (ArticleTag.user_article_id.in_(user_article_ids))
            & (ArticleTag.user_tag_id.in_(tag_name_to_id.values()))
        )
        existing_result = await self.db.execute(existing_pairs_query)
        existing_pairs = {
            (row.user_article_id, row.user_tag_id)
            for row in existing_result.all()
        }

        tags_created = 0
        for article_id, tag_name in article_tag_pairs:
            user_article_id = article_to_user_article.get(article_id)
            if not user_article_id:
                continue
            tag_id = tag_name_to_id[tag_name]
            if (user_article_id, tag_id) in existing_pairs:
                continue

            article_tag = ArticleTag(
                user_article_id=user_article_id, user_tag_id=tag_id
            )
            self.db.add(article_tag)
            tags_created += 1

        if tags_created:
            await self.db.flush()

        return tags_created

"""Application service orchestrating article operations."""

from datetime import date
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

import structlog
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.tag import TagApplication
from backend.core.exceptions import NotFoundError
from backend.domain.article.article import ArticleDomain
from backend.models import User

if TYPE_CHECKING:
    from backend.infrastructure.repositories.article import ArticleMetadata
    from backend.models.user_article import UserArticle

from backend.domain import DEFAULT_LIMIT
from backend.infrastructure.repositories import (
    ArticleRepository,
    FolderRepository,
    UserFeedRepository,
    UserTagRepository,
)
from backend.schemas.core import (
    PaginatedResponse,
    PaginationMetadata,
    ResponseMessage,
)
from backend.schemas.domain import (
    ArticleListResponse,
    ArticleResponse,
    ArticleStateUpdateRequest,
    MarkAllReadRequest,
    TagListResponse,
)
from backend.utils.content import ContentProcessor
from backend.utils.cursor import parse_cursor_data
from backend.utils.text_processing import calculate_reading_time

logger = structlog.get_logger()


class ArticleApplication:
    """Application service for article operations."""

    def __init__(
        self, db: AsyncSession, tag_management: TagApplication | None = None
    ):
        """Initialize the article application with database and optional tag service."""
        self.db = db
        self.repository = ArticleRepository(db)
        self.folder_repository = FolderRepository(db)
        self.user_feed_repository = UserFeedRepository(db)
        self.user_tag_repository = UserTagRepository(db)
        self._tag_management = tag_management

    @property
    def tag_management(self) -> TagApplication:
        """Get TagApplication instance, creating if not injected."""
        if self._tag_management is None:
            self._tag_management = TagApplication(self.db)
        return self._tag_management

    async def get_articles(
        self,
        current_user: User,
        cursor: str | None = None,
        subscription_ids: list[UUID] | None = None,
        is_read: str | None = None,
        tag_ids: list[UUID] | None = None,
        folder_ids: list[UUID] | None = None,
        read_later: str | None = None,
        q: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = DEFAULT_LIMIT,
    ) -> PaginatedResponse[ArticleListResponse]:
        """Get user's articles with optional filters using cursor-based pagination."""
        if folder_ids:
            for folder_id in folder_ids:
                folder = await self.folder_repository.find_by_id(
                    folder_id, current_user.id
                )
                if not folder:
                    raise NotFoundError("Folder not found or access denied")

        if subscription_ids:
            for subscription_id in subscription_ids:
                user_feed = await self.user_feed_repository.find_by_id(
                    subscription_id, current_user.id
                )
                if not user_feed:
                    raise NotFoundError(
                        "Subscription not found or access denied"
                    )

        if tag_ids:
            for tag_id in tag_ids:
                tag = await self.user_tag_repository.find_by_id(
                    tag_id, current_user.id
                )
                if not tag:
                    raise NotFoundError("One or more tags not found")

        has_search = q is not None and q != "*"

        base_query = self.repository.build_articles_base_query(
            current_user=current_user,
            subscription_ids=subscription_ids,
            folder_ids=folder_ids,
            tag_ids=tag_ids,
            is_read=is_read,
            read_later=read_later,
            q=q,
            from_date=from_date,
            to_date=to_date,
        )

        cursor_data = parse_cursor_data(cursor) or {}
        base_query = self.repository.build_cursor_filtering(
            base_query, cursor_data, has_search=has_search, q=q
        )

        result = await self.repository.execute_articles_query(
            base_query, limit, has_search=has_search
        )

        article_ids = [cast(UUID, article.id) for article in result.articles]
        tags_by_article = await self.repository.get_article_tags(
            article_ids, current_user
        )

        response_data = self._build_article_list_response(
            result.articles,
            result.metadata,
            tags_by_article,
        )

        total = await self.repository.get_articles_count(
            current_user,
            subscription_ids=subscription_ids,
            folder_ids=folder_ids,
            tag_ids=tag_ids,
            is_read=is_read,
            read_later=read_later,
            q=q,
            from_date=from_date,
            to_date=to_date,
        )

        return self._build_paginated_response(
            data=response_data,
            total=total,
            limit=limit,
            has_more=result.has_more,
            next_cursor=result.next_cursor,
        )

    async def get_article(
        self, article_id: UUID, current_user: User
    ) -> ArticleResponse:
        """Get specific article details and mark it as read."""
        article_result = await self.repository.get_article_by_id(
            article_id, current_user
        )
        if not article_result:
            raise NotFoundError("Article not found or access denied")

        (
            article,
            subscription_id,
            subscription_title,
            subscription_website,
        ) = article_result

        await self.repository.mark_article_as_read(article_id, current_user)

        state = await self.repository.get_user_article_state(
            article_id, current_user
        )
        article_tags = await self.repository.get_article_tags(
            [article_id], current_user
        )
        tags = article_tags.get(article_id, [])

        return self._build_article_response(
            article=article,
            subscription_id=subscription_id,
            subscription_title=subscription_title,
            subscription_website=subscription_website,
            state=state,
            article_tags=tags,
        )

    async def update_article_state(
        self,
        article_id: UUID,
        state_data: ArticleStateUpdateRequest,
        current_user: User,
    ) -> ResponseMessage:
        """Update user's article state and tags."""
        article_exists = await self.repository.find_by_id(
            article_id, current_user.id
        )
        if not article_exists:
            raise NotFoundError("Article not found or access denied")

        state_updated = await self.repository.update_article_read_state(
            article_id,
            state_data.model_dump(exclude_unset=True, exclude={"tag_ids"}),
            current_user,
        )

        await self._update_article_tags(article_id, state_data, current_user)

        message = ArticleDomain.build_state_update_message(state_updated)

        logger.info(
            "Updated article state",
            user_id=current_user.id,
            article_id=article_id,
            state_updated=state_updated,
        )

        return ResponseMessage(message=message)

    async def mark_all_as_read(
        self, request_data: MarkAllReadRequest, current_user: User
    ) -> ResponseMessage:
        """Mark all articles as read or unread with optional filtering."""
        user_id = current_user.id

        if request_data.folder_ids:
            for folder_id in request_data.folder_ids:
                folder = await self.folder_repository.find_by_id(
                    folder_id, user_id
                )
                if not folder:
                    raise NotFoundError("Folder not found or access denied")

        if request_data.subscription_ids:
            for subscription_id in request_data.subscription_ids:
                user_feed = await self.user_feed_repository.find_by_id(
                    subscription_id, user_id
                )
                if not user_feed:
                    raise NotFoundError(
                        "Subscription not found or access denied"
                    )

        if request_data.tag_ids:
            for tag_id in request_data.tag_ids:
                tag = await self.user_tag_repository.find_by_id(tag_id, user_id)
                if not tag:
                    raise NotFoundError("One or more tags not found")

        query = await self.repository.build_mark_all_articles_query(
            current_user,
            subscription_ids=request_data.subscription_ids,
            folder_ids=request_data.folder_ids,
            tag_ids=request_data.tag_ids,
            is_read_filter=request_data.is_read_filter,
            read_later=request_data.read_later,
            q=request_data.q,
            from_date=request_data.from_date,
            to_date=request_data.to_date,
        )

        await self.repository.bulk_mark_articles(
            current_user,
            [row[0] for row in await self.db.execute(query)],
            request_data.is_read,
        )

        final_message = ArticleDomain.build_mark_all_message(request_data)

        logger.info(
            "Marked articles with read status",
            user_id=current_user.id,
            is_read=request_data.is_read,
            subscription_ids=request_data.subscription_ids,
            folder_ids=request_data.folder_ids,
            tag_ids=request_data.tag_ids,
            is_read_filter=request_data.is_read_filter,
            read_later=request_data.read_later,
            q=request_data.q,
            from_date=request_data.from_date,
            to_date=request_data.to_date,
        )

        return ResponseMessage(message=final_message)

    async def _update_article_tags(
        self,
        article_id: UUID,
        state_data: ArticleStateUpdateRequest,
        current_user: User,
    ) -> None:
        """Update article tags based on state data."""
        if state_data.tag_ids is None:
            return

        await self.tag_management.sync_article_tags(
            current_user.id, article_id, state_data.tag_ids
        )

    def _build_article_list_response(
        self,
        articles: list[Any],
        metadata: dict[UUID, "ArticleMetadata"],
        tags_by_article: dict[UUID, list[Any]],
    ) -> list[ArticleListResponse]:
        """Build article list responses from raw data."""
        from backend.schemas.domain import ArticleFeedList

        response = []
        for article in articles:
            article_id: UUID = cast(UUID, article.id)
            article_meta = metadata.get(article_id)
            if article_meta is None:
                continue

            feeds = [
                ArticleFeedList(
                    id=article_meta.subscription_id,
                    title=article_meta.subscription_title,
                    website=article_meta.subscription_website or "",
                )
            ]

            response.append(
                ArticleListResponse(
                    id=article.id,
                    title=article.title or "",
                    feeds=feeds,
                    media_url=article.media_url,
                    published_at=article.published_at,
                    is_read=article_meta.is_read,
                    read_later=article_meta.read_later,
                    summary=article.summary,
                )
            )
        return response

    def _build_article_response(
        self,
        article: Row[Any],
        subscription_id: UUID,
        subscription_title: str | None,
        subscription_website: str | None,
        state: "UserArticle | None",
        article_tags: list[Any],
    ) -> ArticleResponse:
        """Build single article response."""
        from backend.models import Article
        from backend.schemas.domain import ArticleFeedList

        feeds = [
            ArticleFeedList(
                id=subscription_id,
                title=subscription_title or "",
                website=subscription_website or "",
            )
        ]

        content_to_use = article.content

        reading_time = calculate_reading_time(
            content_to_use
        ) or calculate_reading_time(article.summary)

        return ArticleResponse(
            id=article.id,
            title=article.title or "",
            feeds=feeds,
            media_url=article.media_url,
            published_at=article.published_at,
            is_read=state.is_read if state else False,
            read_later=state.read_later if state else False,
            summary=article.summary,
            author=article.author,
            canonical_url=article.canonical_url or "",
            tags=[
                TagListResponse(
                    id=tag.id,
                    name=tag.name,
                    article_count=tag.article_count,
                )
                for tag in article_tags
            ],
            content=(
                ContentProcessor()._generate_frontend_html(content_to_use)
                if isinstance(article, Article) and content_to_use
                else None
            ),
            reading_time=reading_time,
            platform_metadata=article.platform_metadata or {},
        )

    def _build_paginated_response(
        self,
        data: list[Any],
        total: int,
        limit: int,
        has_more: bool | None = None,
        next_cursor: str | None = None,
    ) -> PaginatedResponse[Any]:
        """Build paginated response with metadata."""
        if has_more is None:
            has_more = len(data) == limit and total > limit

        pagination = PaginationMetadata(
            total=total,
            limit=limit,
            offset=0,
            has_more=has_more,
            next_cursor=next_cursor,
        )

        return PaginatedResponse(data=data, pagination=pagination)

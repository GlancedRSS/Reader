"""Schemas for article management, including listing, details, and state updates."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from backend.schemas.core import ArticleFeedList, BaseSchema
from backend.schemas.domain.tag import TagListResponse


class ArticleListResponse(BaseSchema):
    """GET '/api/v1/articles'."""

    id: UUID
    title: str
    feeds: list[ArticleFeedList] = Field(default_factory=list)
    media_url: str | None = None
    published_at: datetime | None = None
    is_read: bool = False
    read_later: bool = False
    summary: str | None = None


class ArticleResponse(BaseSchema):
    """GET '/api/v1/articles/{article_id}'."""

    id: UUID
    title: str
    feeds: list[ArticleFeedList] = Field(default_factory=list)
    media_url: str | None = None
    published_at: datetime | None = None
    is_read: bool = False
    read_later: bool = False
    summary: str | None = None
    author: str | None = None
    canonical_url: str
    tags: list[TagListResponse] = Field(default_factory=list)
    content: str | None = Field(None)
    reading_time: int | None = Field(
        None, description="Estimated reading time in minutes"
    )
    platform_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Platform-specific metadata (YouTube, Vimeo, etc.)",
    )


class ArticleStateUpdateRequest(BaseSchema):
    """PUT '/api/v1/articles/{article_id}'."""

    is_read: bool | None = Field(None)
    read_later: bool | None = Field(None)
    tag_ids: list[UUID] | None = Field(None)


class MarkAllReadRequest(BaseSchema):
    """POST '/api/v1/articles/mark-as-read'.

    Supports the same filtering parameters as GET /api/v1/articles/ to allow
    marking filtered subsets of articles (e.g., search results, date ranges).
    """

    is_read: bool = Field(default=True)
    subscription_ids: list[UUID] | None = Field(None)
    folder_ids: list[UUID] | None = Field(None)
    tag_ids: list[UUID] | None = Field(None)
    is_read_filter: str | None = Field(None, pattern="^(read|unread)$")
    read_later: str | None = Field(None, pattern="^(true|false)$")
    q: str | None = Field(None, min_length=1, max_length=128)
    from_date: date | None = Field(None)
    to_date: date | None = Field(None)

from typing import Literal
from uuid import UUID

from pydantic import Field

from backend.domain import MAX_LIMIT
from backend.schemas.core import (
    BaseSchema,
    ListResponse,
    PaginatedResponse,
)
from backend.schemas.domain.article import ArticleListResponse

MIN_SEARCH_QUERY_LENGTH = 1
"""Minimum length for search queries (autocomplete support)."""

MAX_SEARCH_QUERY_LENGTH = 128
"""Maximum length for search queries."""

DEFAULT_SEARCH_LIMIT = 20
"""Default number of results per search type."""

MAX_SEARCH_PER_TYPE = 20
"""Maximum number of results per search type."""


class UnifiedSearchRequest(BaseSchema):
    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )


class FeedSearchRequest(BaseSchema):
    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )
    limit: int = Field(default=DEFAULT_SEARCH_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)


class TagSearchRequest(BaseSchema):
    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class FolderSearchRequest(BaseSchema):
    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class FeedSearchHit(BaseSchema):
    id: UUID = Field(...)
    title: str = Field(...)
    website: str | None = Field(None)
    is_active: bool = Field(True)
    is_pinned: bool = Field(False)
    unread_count: int = Field(0)


class TagSearchHit(BaseSchema):
    id: UUID = Field(...)
    name: str = Field(...)
    article_count: int = Field(0)


class FolderSearchHit(BaseSchema):
    id: UUID = Field(...)
    name: str = Field(...)
    unread_count: int = Field(0)
    is_pinned: bool = Field(False)


class UnifiedSearchHit(BaseSchema):
    type: Literal["article", "feed", "tag", "folder"] = Field(...)
    data: (
        ArticleListResponse | FeedSearchHit | TagSearchHit | FolderSearchHit
    ) = Field(...)


class UnifiedSearchResponse(ListResponse[UnifiedSearchHit]):
    pass


class FeedSearchResponse(PaginatedResponse[FeedSearchHit]):
    pass


class TagSearchResponse(PaginatedResponse[TagSearchHit]):
    pass


class FolderSearchResponse(PaginatedResponse[FolderSearchHit]):
    pass

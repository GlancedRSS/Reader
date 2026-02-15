"""Request and response schemas for universal search."""

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
    """Request for universal search across all content types.

    Used by GET /api/v1/search?q={query}
    Returns up to 20 results total, no pagination.
    """

    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )


class FeedSearchRequest(BaseSchema):
    """Request for feed-specific search.

    Used by GET /api/v1/search/feeds
    """

    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )
    limit: int = Field(default=DEFAULT_SEARCH_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)


class TagSearchRequest(BaseSchema):
    """Request for tag-specific search.

    Used by GET /api/v1/search/tags
    """

    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class FolderSearchRequest(BaseSchema):
    """Request for folder-specific search.

    Used by GET /api/v1/search/folders
    """

    query: str = Field(
        ...,
        min_length=MIN_SEARCH_QUERY_LENGTH,
        max_length=MAX_SEARCH_QUERY_LENGTH,
    )
    limit: int = Field(default=20, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class FeedSearchHit(BaseSchema):
    """Single feed search result."""

    id: UUID = Field(...)
    title: str = Field(...)
    website: str | None = Field(None)
    is_active: bool = Field(True)
    is_pinned: bool = Field(False)
    unread_count: int = Field(0)


class TagSearchHit(BaseSchema):
    """Single tag search result."""

    id: UUID = Field(...)
    name: str = Field(...)
    article_count: int = Field(0)


class FolderSearchHit(BaseSchema):
    """Single folder search result."""

    id: UUID = Field(...)
    name: str = Field(...)
    unread_count: int = Field(0)
    is_pinned: bool = Field(False)


class UnifiedSearchHit(BaseSchema):
    """Single hit from universal search with type discriminator.

    The 'type' field indicates the structure of 'data':
    - article: data is ArticleListResponse
    - feed: data is FeedSearchHit
    - tag: data is TagSearchHit
    - folder: data is FolderSearchHit
    """

    type: Literal["article", "feed", "tag", "folder"] = Field(...)
    data: (
        ArticleListResponse | FeedSearchHit | TagSearchHit | FolderSearchHit
    ) = Field(...)


class UnifiedSearchResponse(ListResponse[UnifiedSearchHit]):
    """Response from universal search endpoint.

    Contains top 20 results mixed together, ranked by relevance.
    No pagination - always returns up to 20 results.
    """


class FeedSearchResponse(PaginatedResponse[FeedSearchHit]):
    """Response from feed-specific search."""

    pass


class TagSearchResponse(PaginatedResponse[TagSearchHit]):
    """Response from tag-specific search."""

    pass


class FolderSearchResponse(PaginatedResponse[FolderSearchHit]):
    """Response from folder-specific search."""

    pass

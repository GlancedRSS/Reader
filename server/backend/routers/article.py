"""Article management endpoints for reading and organizing content."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.core.dependencies import get_article_application
from backend.core.fastapi import get_user_from_request_state
from backend.domain import DEFAULT_LIMIT, MAX_LIMIT
from backend.models import User
from backend.schemas.core import PaginatedResponse, ResponseMessage
from backend.schemas.domain import (
    ArticleListResponse,
    ArticleResponse,
    ArticleStateUpdateRequest,
    MarkAllReadRequest,
)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[ArticleListResponse],
    summary="List articles",
    description="Get user's articles with optional filters and search using cursor-based pagination.",
    tags=["Articles"],
)
async def get_articles(
    cursor: str | None = Query(
        None,
        description="Pagination cursor for fetching next page of articles. Use for infinite scroll pagination.",
    ),
    subscription_ids: list[UUID] | None = Query(
        None, description="Filter by subscription IDs"
    ),
    is_read: str | None = Query(
        default=None,
        pattern="^(read|unread)$",
        description="Filter by read state: 'read' for read articles, 'unread' for unread articles. If not provided, shows all articles",
    ),
    tag_ids: list[UUID] | None = Query(
        None,
        description="Filter by tag IDs.",
    ),
    folder_ids: list[UUID] | None = Query(
        None, description="Filter by folder IDs"
    ),
    read_later: str | None = Query(
        default=None,
        pattern="^(true|false)$",
        description="Filter by read later state: 'true' for read later articles, 'false' for articles not marked as read later. If not provided, shows all articles",
    ),
    q: str | None = Query(
        None,
        min_length=1,
        max_length=128,
        description="Search query string for full-text search",
    ),
    from_date: date | None = Query(
        None,
        description="Filter articles published on or after this date (ISO 8601)",
    ),
    to_date: date | None = Query(
        None,
        description="Filter articles published on or before this date (ISO 8601)",
    ),
    limit: int = Query(
        default=DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description="Number of articles to return",
    ),
    article_app=Depends(get_article_application),
    current_user: User = Depends(get_user_from_request_state),
) -> PaginatedResponse[ArticleListResponse]:
    """Get user's articles with optional filters and cursor-based pagination."""
    return await article_app.get_articles(
        current_user=current_user,
        cursor=cursor,
        subscription_ids=subscription_ids,
        is_read=is_read,
        tag_ids=tag_ids,
        folder_ids=folder_ids,
        read_later=read_later,
        q=q,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="Get article details",
    description="Get specific article details.",
    tags=["Articles"],
)
async def get_article(
    article_id: UUID,
    article_app=Depends(get_article_application),
    current_user: User = Depends(get_user_from_request_state),
) -> ArticleResponse:
    """Get specific article details."""
    return await article_app.get_article(article_id, current_user)


@router.put(
    "/{article_id}",
    response_model=ResponseMessage,
    summary="Update article state",
    description="Update user's article state (read/unread, bookmark/unbookmark) and tags.",
    tags=["Articles"],
)
async def update_article_state(
    article_id: UUID,
    state_data: ArticleStateUpdateRequest,
    article_app=Depends(get_article_application),
    current_user: User = Depends(get_user_from_request_state),
) -> ResponseMessage:
    """Update user's article state (read/unread, bookmark/unbookmark) and tags."""
    return await article_app.update_article_state(
        article_id, state_data, current_user
    )


@router.post(
    "/mark-as-read",
    response_model=ResponseMessage,
    summary="Mark all as read",
    description="Mark all articles as read or unread for the current user with optional filtering.",
    tags=["Articles"],
)
async def mark_all_as_read(
    request_data: MarkAllReadRequest,
    article_app=Depends(get_article_application),
    current_user: User = Depends(get_user_from_request_state),
) -> ResponseMessage:
    """Mark all articles as read or unread for the current user with optional filtering."""
    return await article_app.mark_all_as_read(request_data, current_user)

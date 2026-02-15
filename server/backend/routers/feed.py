"""User feed management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.core.dependencies import get_feed_application
from backend.core.fastapi import get_user_from_request_state
from backend.domain import DEFAULT_LIMIT, MAX_LIMIT
from backend.models import User
from backend.schemas.core import PaginatedResponse, ResponseMessage
from backend.schemas.domain import (
    UserFeedListResponse,
    UserFeedResponse,
    UserFeedUpdateRequest,
)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[UserFeedListResponse],
    summary="List user feeds",
    description="Get user's feeds with optional folder filtering and pagination.",
    tags=["Feeds"],
)
async def get_user_feeds(
    limit: int = Query(
        default=DEFAULT_LIMIT,
        le=MAX_LIMIT,
        description="Number of feeds to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of feeds to skip (used for alphabetical ordering)",
    ),
    folder_id: UUID | None = Query(
        default=None,
        description="Filter feeds by folder ID. If not provided, returns feeds without folder assignment (unless all=True)",
    ),
    all: bool = Query(
        default=False,
        description="Return all feeds regardless of folder assignment. When true, folder_id is ignored",
    ),
    order_by: str | None = Query(
        default=None,
        pattern="^(name|recent)$",
        description="Order feeds: 'name' for alphabetical A-Z with offset pagination, 'recent' for cursor-based pagination (newest articles first)",
    ),
    cursor: str | None = Query(
        default=None,
        description="Pagination cursor for fetching next page when order_by='recent'",
    ),
    feed_app=Depends(get_feed_application),
    current_user: User = Depends(get_user_from_request_state),
) -> PaginatedResponse[UserFeedListResponse]:
    """Get user's feeds with optional folder filtering and pagination."""
    user_id = current_user.id
    return await feed_app.get_user_feeds_paginated(
        user_id,
        folder_id,
        order_by,
        limit,
        offset,
        cursor,
        all,
    )


@router.get(
    "/{user_feed_id}",
    response_model=UserFeedResponse,
    summary="Get user feed details",
    description="Get user feed details by user feed ID.",
    tags=["Feeds"],
)
async def get_user_feed(
    user_feed_id: UUID,
    feed_app=Depends(get_feed_application),
    current_user: User = Depends(get_user_from_request_state),
) -> UserFeedResponse:
    """Get user feed details by user feed ID."""
    user_id = current_user.id
    return await feed_app.get_user_feed_by_id(
        user_feed_id,
        user_id,
    )


@router.put(
    "/{user_feed_id}",
    response_model=ResponseMessage,
    summary="Update user feed",
    description="Update user's feed by user feed ID.",
    tags=["Feeds"],
)
async def update_user_feed(
    user_feed_id: UUID,
    user_feed_data: UserFeedUpdateRequest,
    feed_app=Depends(get_feed_application),
    current_user: User = Depends(get_user_from_request_state),
) -> ResponseMessage:
    """Update user's feed by user feed ID."""
    user_id = current_user.id
    return await feed_app.update_user_feed(
        user_feed_id,
        user_feed_data,
        user_id,
    )


@router.delete(
    "/{user_feed_id}",
    response_model=ResponseMessage,
    summary="Unsubscribe",
    description="Unsubscribe from feed by user feed ID. This will delete the subscription and remove articles that aren't accessible via other feeds.",
    tags=["Feeds"],
)
async def unsubscribe(
    user_feed_id: UUID,
    feed_app=Depends(get_feed_application),
    current_user: User = Depends(get_user_from_request_state),
) -> ResponseMessage:
    """Unsubscribe by user feed ID."""
    user_id = current_user.id
    return await feed_app.unsubscribe_from_feed(
        user_feed_id,
        user_id,
    )

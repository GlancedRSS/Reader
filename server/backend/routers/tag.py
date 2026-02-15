"""Tag management for article categorization and organization."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.core.dependencies import get_tag_application
from backend.core.fastapi import get_user_from_request_state
from backend.domain import DEFAULT_LIMIT, MAX_LIMIT
from backend.models import User
from backend.schemas.core import PaginatedResponse, ResponseMessage
from backend.schemas.domain import (
    TagCreateRequest,
    TagListResponse,
    TagUpdateRequest,
)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[TagListResponse],
    summary="List tags",
    description="Get tags for the current user with pagination.",
    tags=["Tags"],
)
async def get_user_tags(
    current_user: User = Depends(get_user_from_request_state),
    tag_app=Depends(get_tag_application),
    limit: int = Query(
        default=DEFAULT_LIMIT,
        le=MAX_LIMIT,
        description="Number of tags to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of tags to skip (for alphabetical pagination)",
    ),
) -> PaginatedResponse[TagListResponse]:
    """Get tags for the current user with pagination."""
    return await tag_app.get_user_tags(current_user.id, limit, offset)


@router.post(
    "",
    response_model=TagListResponse,
    summary="Create tag",
    description="Create a new user tag (get-or-create pattern to handle unique constraint).",
    tags=["Tags"],
)
async def create_user_tag(
    tag_data: TagCreateRequest,
    current_user: User = Depends(get_user_from_request_state),
    tag_app=Depends(get_tag_application),
) -> TagListResponse:
    """Create a new user tag (get-or-create pattern to handle unique constraint)."""
    return await tag_app.create_user_tag(current_user.id, tag_data)


@router.get(
    "/{tag_id}",
    response_model=TagListResponse,
    summary="Get tag",
    description="Get a specific tag by ID.",
    tags=["Tags"],
)
async def get_user_tag(
    tag_id: UUID,
    current_user: User = Depends(get_user_from_request_state),
    tag_app=Depends(get_tag_application),
) -> TagListResponse:
    """Get a specific tag for the current user."""
    return await tag_app.get_user_tag(current_user.id, tag_id)


@router.put(
    "/{tag_id}",
    response_model=ResponseMessage,
    summary="Update tag",
    description="Update a user tag.",
    tags=["Tags"],
)
async def update_user_tag(
    tag_id: UUID,
    tag_data: TagUpdateRequest,
    current_user: User = Depends(get_user_from_request_state),
    tag_app=Depends(get_tag_application),
) -> ResponseMessage:
    """Update a user tag."""
    return await tag_app.update_user_tag(current_user.id, tag_id, tag_data)


@router.delete(
    "/{tag_id}",
    response_model=ResponseMessage,
    summary="Delete tag",
    description="Delete a user tag.",
    tags=["Tags"],
)
async def delete_user_tag(
    tag_id: UUID,
    current_user: User = Depends(get_user_from_request_state),
    tag_app=Depends(get_tag_application),
) -> ResponseMessage:
    """Delete a user tag."""
    return await tag_app.delete_user_tag(current_user.id, tag_id)

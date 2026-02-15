"""Schemas for user tag management, including creation and updates."""

from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class TagListResponse(BaseSchema):
    """GET '/api/v1/tags'."""

    id: UUID
    name: str
    article_count: int = Field(
        default=0, description="Number of articles with this tag"
    )


class TagCreateRequest(BaseSchema):
    """POST '/api/v1/tags'."""

    name: str = Field(..., min_length=1, max_length=64)


class TagUpdateRequest(BaseSchema):
    """PUT '/api/v1/tags/{tag_id}'."""

    name: str | None = Field(None, min_length=1, max_length=64)

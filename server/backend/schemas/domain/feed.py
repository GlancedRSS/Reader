"""Schemas for user feed subscriptions."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class UserFeedListResponse(BaseSchema):
    """GET '/api/v1/feeds'."""

    id: UUID
    title: str
    unread_count: int = 0
    status: Literal["healthy", "error", "stale"] = "healthy"
    website: str | None = None
    is_pinned: bool = False
    is_active: bool = True


class UserFeedResponse(BaseSchema):
    """GET '/api/v1/feeds/{feed_id}'."""

    title: str
    unread_count: int = 0
    status: Literal["healthy", "error", "stale"] = "healthy"
    website: str | None = None
    is_pinned: bool = False
    is_active: bool = True
    folder_id: UUID | None = None
    folder_name: str | None = None
    language: str | None = Field(None)
    last_update: datetime | None = None

    description: str | None = None
    canonical_url: str | None = None


class UserFeedUpdateRequest(BaseSchema):
    """PUT '/api/v1/feeds/{feed_id}'."""

    title: str | None = Field(None, max_length=200)
    is_pinned: bool | None = Field(None)
    folder_id: UUID | None = Field(None)
    is_active: bool | None = Field(None)

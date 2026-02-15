"""Schemas for folder management, including hierarchical organization and feed assignment."""

from typing import Any
from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class FeedInFolderResponse(BaseSchema):
    """Feed within a folder context for tree response."""

    id: UUID
    title: str
    unread_count: int = 0
    website: str | None = None
    is_pinned: bool = False
    is_active: bool = True


class FolderListResponse(BaseSchema):
    """GET '/api/v1/folders'."""

    id: UUID
    name: str
    parent_id: UUID | None = None
    feed_count: int = 0
    unread_count: int = 0
    is_pinned: bool = False
    depth: int = Field(0, ge=0, le=9)


class FolderCreateRequest(BaseSchema):
    """POST '/api/v1/folders'."""

    name: str = Field(..., min_length=1, max_length=16)
    parent_id: UUID | None = Field(None)


class FolderResponse(BaseSchema):
    """GET '/api/v1/folders/{folder_id}'."""

    id: UUID = Field(...)
    name: str = Field(...)
    parent_id: UUID | None = Field(None)
    feed_count: int = Field(0)
    unread_count: int = Field(0)
    is_pinned: bool = Field(False)
    depth: int = Field(0, ge=0, le=9)
    data: list["FolderListResponse"] = Field(default_factory=list)
    pagination: dict[str, Any] = Field()


class FolderUpdateRequest(BaseSchema):
    """PUT '/api/v1/folders/{folder_id}'."""

    name: str | None = Field(None, min_length=1, max_length=16)
    parent_id: UUID | None = Field(None)
    is_pinned: bool | None = Field(None)


class FolderTreeResponse(BaseSchema):
    """GET '/api/v1/folders/tree' - Complete folder hierarchy."""

    id: UUID | None = None
    name: str
    parent_id: UUID | None = None
    feed_count: int = 0
    unread_count: int = 0
    is_pinned: bool = False
    depth: int = Field(0, ge=0, le=9)
    feeds: list[FeedInFolderResponse] = Field(default_factory=list)
    subfolders: list["FolderTreeResponse"] = Field(default_factory=list)

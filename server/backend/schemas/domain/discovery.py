"""Schemas for feed discovery operations."""

from typing import Literal
from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class FeedDiscoveryRequest(BaseSchema):
    """POST '/api/v1/discovery'."""

    url: str = Field(..., pattern=r"^https?://")
    folder_id: UUID | None = Field(None)


class FeedDiscoveryResponse(BaseSchema):
    """POST '/api/v1/discovery'."""

    status: Literal["existing", "moved", "subscribed", "pending", "failed"] = (
        Field(...)
    )
    message: str = Field(...)

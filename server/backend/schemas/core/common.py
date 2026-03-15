from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from backend.schemas.core import BaseSchema

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    total: int | None = Field(
        None,
        description="Total number of items available (optional for cursor-based)",
    )
    limit: int | None = Field(
        None, description="Number of items per page (optional for cursor-based)"
    )
    offset: int | None = Field(
        None,
        description="Number of items skipped (legacy field for backward compatibility)",
    )
    has_more: bool = Field(..., description="Whether more items are available")
    next_cursor: str | None = Field(
        None,
        description="Pagination cursor for fetching next page (cursor-based pagination)",
    )


class ResponseMessage(BaseModel):
    message: str = Field(..., description="Success message")


class PaginatedResponse[T](BaseSchema):
    data: list[T] = Field(..., description="List of items for current page")
    pagination: PaginationMetadata = Field(
        ..., description="Pagination metadata"
    )


class ListResponse[T](BaseSchema):
    data: list[T] = Field(..., description="List of items")


class ArticleFeedList(BaseSchema):
    id: UUID
    title: str
    website: str


class ErrorResponse(BaseSchema):
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        None, description="Additional error details"
    )
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: UUID | None = Field(None, description="Request ID for tracing")


__all__ = [
    "ErrorResponse",
    "ListResponse",
    "PaginatedResponse",
    "PaginationMetadata",
    "ResponseMessage",
]

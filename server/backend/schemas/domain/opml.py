"""Schemas for OPML feed import/export operations and file management."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class OpmlOperationListResponse(BaseSchema):
    """GET '/api/v1/opml'."""

    id: UUID = Field(...)
    type: Literal["import", "export"] = Field(...)
    status: str = Field(...)
    filename: str | None = Field(None)
    file_size: int | None = Field(None)
    created_at: datetime = Field(...)


class OpmlOperationResponse(BaseSchema):
    """GET '/api/v1/opml/status/{job_id}'."""

    id: UUID = Field(...)
    type: Literal["import", "export"] = Field(...)
    status: str = Field(...)
    filename: str | None = Field(None)
    created_at: datetime = Field(...)
    completed_at: datetime | None = Field(None)
    total_feeds: int = Field(0)
    imported_feeds: int = Field(0)
    failed_feeds: int = Field(0)
    duplicate_feeds: int = Field(0)
    failed_feeds_log: dict[str, Any] | list[Any] | None = Field(None)


class OpmlUploadResponse(BaseSchema):
    """POST '/api/v1/opml/upload'."""

    import_id: UUID = Field(...)
    filename: str = Field(...)
    file_size: int = Field(..., ge=0, le=16777216)
    message: str = Field(...)


class OpmlImport(BaseSchema):
    """Utilised after OPML file upload."""

    import_id: UUID = Field(...)
    folder_id: UUID | None = Field(None)


class OpmlExportRequest(BaseSchema):
    """POST '/api/v1/opml/export'."""

    folder_id: UUID | None = Field(None)

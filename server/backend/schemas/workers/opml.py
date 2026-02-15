"""OPML job schemas.

Schemas for OPML import and export jobs.
"""

from pydantic import Field

from backend.schemas.workers.base import BaseJobRequest, BaseJobResponse


class OpmlImportJobRequest(BaseJobRequest):
    """Request for OPML import job."""

    user_id: str = Field(..., description="User ID (UUID)")
    import_id: str = Field(..., description="Import record ID (UUID)")
    storage_key: str = Field(..., description="Local storage key for OPML file")
    filename: str = Field(..., description="Original filename")
    folder_id: str | None = Field(
        default=None, description="Default folder ID for imports"
    )


class OpmlImportJobResponse(BaseJobResponse):
    """Response for OPML import job."""

    total_feeds: int = Field(default=0, description="Total feeds in OPML")
    imported_feeds: int = Field(
        default=0, description="Successfully imported feeds"
    )
    failed_feeds: int = Field(
        default=0, description="Feeds that failed to import"
    )
    duplicate_feeds: int = Field(
        default=0, description="Feeds already subscribed"
    )


class OpmlExportJobRequest(BaseJobRequest):
    """Request for OPML export job."""

    user_id: str = Field(..., description="User ID (UUID)")
    export_id: str = Field(..., description="Export record ID")
    folder_id: str | None = Field(
        default=None, description="Optional folder ID to filter"
    )


class OpmlExportJobResponse(BaseJobResponse):
    """Response for OPML export job."""

    total_feeds: int = Field(..., description="Number of feeds exported")
    file_size: int = Field(..., description="OPML file size in bytes")
    download_url: str | None = Field(
        default=None, description="Presigned download URL"
    )
    filename: str | None = Field(default=None, description="Generated filename")

"""Base job request and response schemas."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class BaseJobRequest(BaseModel):
    """Base request schema for all jobs."""

    job_id: str = Field(
        default_factory=lambda: (
            f"scheduled-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        ),
        description="Unique job identifier for tracking",
    )


class BaseJobResponse(BaseModel):
    """Base response schema for all jobs."""

    job_id: str = Field(..., description="Job identifier echoed from request")
    status: str = Field(
        ..., description="Job status: success, error, or failed"
    )
    message: str | None = Field(
        default=None, description="Human-readable status message"
    )
    error: str | None = Field(
        default=None, description="Error message if status is error/failed"
    )

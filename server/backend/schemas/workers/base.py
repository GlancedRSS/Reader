"""Base job request and response schemas.

All job schemas inherit from these base classes.
"""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class BaseJobRequest(BaseModel):
    """Base request schema for all jobs.

    All job requests include a job_id for tracking purposes.
    For scheduled jobs, job_id is auto-generated if not provided.
    """

    job_id: str = Field(
        default_factory=lambda: (
            f"scheduled-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        ),
        description="Unique job identifier for tracking",
    )


class BaseJobResponse(BaseModel):
    """Base response schema for all jobs.

    All job responses include job_id, status, and optional message.
    """

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

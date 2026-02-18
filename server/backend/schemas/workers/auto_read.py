"""Auto-read job schemas."""

from pydantic import Field

from backend.schemas.workers.base import BaseJobRequest, BaseJobResponse


class AutoMarkReadJobRequest(BaseJobRequest):
    """Request for auto-mark as read job."""

    user_id: str | None = Field(
        default=None, description="Specific user ID, or None for all users"
    )


class AutoMarkReadJobResponse(BaseJobResponse):
    """Response for auto-mark as read job."""

    users_processed: int = Field(..., description="Number of users processed")
    articles_marked_read: int = Field(
        ..., description="Total articles marked as read"
    )
    users_skipped: int = Field(
        ..., description="Users with no articles to mark"
    )

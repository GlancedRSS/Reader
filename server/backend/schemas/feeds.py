"""Request and response schemas for feed job endpoints."""

from pydantic import BaseModel, Field


class FeedCreateAndSubscribeJobRequest(BaseModel):
    """Request body for feed creation and subscription job."""

    job_id: str
    url: str
    user_id: str
    folder_id: str | None = None


class FeedJobResponse(BaseModel):
    """Response for feed jobs with job tracking."""

    job_id: str
    status: str
    action: str | None = None
    subscription_id: str | None = None
    feed_id: str | None = None
    feed_title: str | None = None
    folder_id: str | None = None


class DiscoveryFeedCreateRequest(BaseModel):
    """Internal schema for creating feeds during discovery process."""

    url: str = Field(
        ..., pattern=r"^https?://", description="RSS/Atom feed URL"
    )
    title: str | None = Field(None, description="Feed title")


class FeedUpdateRequest(BaseModel):
    """Internal schema for updating feeds during discovery process."""

    title: str | None = Field(None, description="Feed title")
    description: str | None = Field(None, description="Feed description")
    is_active: bool | None = Field(None, description="Whether feed is active")

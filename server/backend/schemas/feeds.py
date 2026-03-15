from pydantic import BaseModel, Field


class FeedCreateAndSubscribeJobRequest(BaseModel):
    job_id: str
    url: str
    user_id: str
    folder_id: str | None = None


class FeedJobResponse(BaseModel):
    job_id: str
    status: str
    action: str | None = None
    subscription_id: str | None = None
    feed_id: str | None = None
    feed_title: str | None = None
    folder_id: str | None = None


class DiscoveryFeedCreateRequest(BaseModel):
    url: str = Field(
        ..., pattern=r"^https?://", description="RSS/Atom feed URL"
    )
    title: str | None = Field(None, description="Feed title")


class FeedUpdateRequest(BaseModel):
    title: str | None = Field(None, description="Feed title")
    description: str | None = Field(None, description="Feed description")
    is_active: bool | None = Field(None, description="Whether feed is active")

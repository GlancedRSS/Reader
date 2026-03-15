from pydantic import Field

from backend.schemas.workers.base import BaseJobRequest, BaseJobResponse


class FeedCleanupJobRequest(BaseJobRequest):
    pass


class FeedCleanupJobResponse(BaseJobResponse):
    orphaned_subscriptions: int = Field(
        ..., description="Orphaned subscriptions cleaned"
    )
    inactive_feeds: int = Field(..., description="Inactive feeds found")


class ScheduledFeedRefreshCycleJobRequest(BaseJobRequest):
    pass


class ScheduledFeedRefreshCycleJobResponse(BaseJobResponse):
    feeds_total: int = Field(..., description="Total feeds to refresh")
    feeds_processed: int = Field(
        ..., description="Feeds processed (success + failed)"
    )
    feeds_successful: int = Field(
        ..., description="Feeds successfully refreshed"
    )
    feeds_failed: int = Field(..., description="Feeds that failed to refresh")
    new_articles_total: int = Field(
        default=0, description="Total new articles found"
    )
    duration_seconds: float = Field(..., description="Total execution time")

"""Scheduled maintenance job schemas.

Schemas for feed cleanup and feed refresh jobs.
"""

from pydantic import Field

from backend.schemas.workers.base import BaseJobRequest, BaseJobResponse


class FeedCleanupJobRequest(BaseJobRequest):
    """Request for feed cleanup job."""

    pass


class FeedCleanupJobResponse(BaseJobResponse):
    """Response for feed cleanup job."""

    orphaned_subscriptions: int = Field(
        ..., description="Orphaned subscriptions cleaned"
    )
    inactive_feeds: int = Field(..., description="Inactive feeds found")


class ScheduledFeedRefreshCycleJobRequest(BaseJobRequest):
    """Request for scheduled feed refresh cycle job."""

    pass


class ScheduledFeedRefreshCycleJobResponse(BaseJobResponse):
    """Response for scheduled feed refresh cycle job."""

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

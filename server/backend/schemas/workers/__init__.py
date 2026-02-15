"""Job request and response schemas.

This module provides Pydantic models for all background job requests and responses.
All schemas follow a consistent pattern with job_id tracking.

Usage:
    from backend.schemas.workers import (
        OpmlImportJobRequest,
    )

    from backend.schemas.workers.opml import OpmlImportJobRequest
"""

from .auto_read import (
    AutoMarkReadJobRequest,
    AutoMarkReadJobResponse,
)
from .base import BaseJobRequest, BaseJobResponse
from .opml import (
    OpmlExportJobRequest,
    OpmlExportJobResponse,
    OpmlImportJobRequest,
    OpmlImportJobResponse,
)
from .scheduled import (
    FeedCleanupJobRequest,
    FeedCleanupJobResponse,
    ScheduledFeedRefreshCycleJobRequest,
    ScheduledFeedRefreshCycleJobResponse,
)

__all__ = [  # noqa: RUF022
    "BaseJobRequest",
    "BaseJobResponse",
    "OpmlImportJobRequest",
    "OpmlImportJobResponse",
    "OpmlExportJobRequest",
    "OpmlExportJobResponse",
    "AutoMarkReadJobRequest",
    "AutoMarkReadJobResponse",
    "FeedCleanupJobRequest",
    "FeedCleanupJobResponse",
    "ScheduledFeedRefreshCycleJobRequest",
    "ScheduledFeedRefreshCycleJobResponse",
]

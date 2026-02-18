"""Job request and response schemas."""

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

"""Status enumerations for feeds, subscriptions, users, and OPML imports."""

from enum import StrEnum


class FeedStatus(StrEnum):
    """Feed health status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PAUSED = "paused"


class SubscriptionStatus(StrEnum):
    """Subscription status values."""

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"


class OpmlImportStatus(StrEnum):
    """OPML import job status values."""

    UPLOADED = "uploaded"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"

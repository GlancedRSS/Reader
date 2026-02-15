"""Status enumerations for feeds, subscriptions, users, and OPML imports."""

from enum import StrEnum


class FeedStatus(StrEnum):
    """Feed health status values.

    Attributes:
        ACTIVE: Feed is being fetched successfully
        INACTIVE: Feed has been paused by the user
        ERROR: Feed has encountered fetching errors
        PAUSED: Feed is temporarily paused by the system

    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PAUSED = "paused"


class SubscriptionStatus(StrEnum):
    """Subscription status values.

    Attributes:
        ACTIVE: User is actively subscribed to the feed
        PAUSED: User has paused the subscription
        ERROR: Subscription has encountered errors
        UNSUBSCRIBED: User has unsubscribed from the feed
        FAILED: Subscription failed during creation/update

    """

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"


class OpmlImportStatus(StrEnum):
    """OPML import job status values.

    Attributes:
        UPLOADED: OPML file has been uploaded but not yet processed
        PENDING: Import job is queued for processing
        PROCESSING: Import job is currently being processed
        COMPLETED: Import job completed successfully
        COMPLETED_WITH_ERRORS: Import completed but some feeds failed
        FAILED: Import job failed entirely

    """

    UPLOADED = "uploaded"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"

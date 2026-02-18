"""Feed health status calculation."""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import structlog

logger = structlog.get_logger()


class FeedDomain:
    """Feed health status calculation."""

    @staticmethod
    def calculate_feed_status(
        feed: Any,
    ) -> Literal["healthy", "error", "stale"]:
        """Calculate feed health: error (error after fetch), stale (no fetch >1hr), healthy."""
        now = datetime.now(UTC)
        status: Literal["healthy", "error", "stale"] = "healthy"

        if not feed:
            return "error"

        if feed.last_error_at and feed.last_fetched_at:
            if feed.last_error_at > feed.last_fetched_at:
                status = "error"
        elif feed.last_error_at and not feed.last_fetched_at:
            status = "error"

        if status == "healthy" and feed.last_fetched_at:
            time_since_fetch = now - feed.last_fetched_at
            if time_since_fetch > timedelta(hours=1):
                status = "stale"
        elif status == "healthy" and not feed.last_fetched_at:
            status = "stale"

        return status

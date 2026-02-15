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
        """Calculate the health status of a feed.

        Status determination:
        - "error": Last error occurred after last successful fetch
        - "stale": No successful fetch in over 1 hour, or never fetched
        - "healthy": Recent successful fetch with no errors

        Args:
            feed: The feed object to check

        Returns:
            Literal["healthy", "stale", "error"]

        """
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

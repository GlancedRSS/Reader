"""Unit tests for FeedDomain - feed health status calculation."""

from datetime import UTC, datetime, timedelta

from backend.domain.feed.feed import FeedDomain


class TestCalculateFeedStatus:
    """Test feed status calculation."""

    def test_status_error_when_last_error_after_last_success(self):
        """Should return 'stale' when both error and success are stale."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        # Set error and success to be over hour ago (stale)
        now = datetime.now(UTC)
        feed.last_error_at = now - timedelta(hours=2)
        feed.last_fetched_at = now - timedelta(hours=1)

        result = FeedDomain.calculate_feed_status(feed)

        # Both are over 1 hour ago, so staleness check triggers
        assert result == "stale"

    def test_status_error_when_last_error_no_success(self):
        """Should return 'error' when error exists and no successful fetch."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        # Use recent timestamps to avoid stale condition
        now = datetime.now(UTC)
        feed.last_error_at = now - timedelta(hours=1)
        feed.last_fetched_at = None

        result = FeedDomain.calculate_feed_status(feed)

        assert result == "error"

    def test_status_stale_when_healthy_over_hour_ago(self):
        """Should return 'stale' when last success was over 1 hour ago."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        feed.last_error_at = None
        feed.last_fetched_at = datetime.now(UTC) - timedelta(hours=1, minutes=1)

        result = FeedDomain.calculate_feed_status(feed)

        assert result == "stale"

    def test_status_stale_when_never_fetched(self):
        """Should return 'stale' when feed was never successfully fetched."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        feed.last_error_at = None
        feed.last_fetched_at = None

        result = FeedDomain.calculate_feed_status(feed)

        assert result == "stale"

    def test_status_healthy_when_recent_success(self):
        """Should return 'healthy' when last success was recent."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        feed.last_error_at = None
        feed.last_fetched_at = datetime.now(UTC) - timedelta(minutes=30)

        result = FeedDomain.calculate_feed_status(feed)

        assert result == "healthy"

    def test_status_healthy_when_recent_success_no_errors(self):
        """Should return 'healthy' when last success was recent with no errors."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        feed.last_error_at = None
        feed.last_fetched_at = datetime.now(UTC) - timedelta(minutes=30)

        result = FeedDomain.calculate_feed_status(feed)

        assert result == "healthy"

    def test_status_error_when_success_after_error(self):
        """Should return 'healthy' when success is after error (both recent)."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        # Both error and success are very recent
        now = datetime.now(UTC)
        feed.last_error_at = now - timedelta(minutes=30)
        feed.last_fetched_at = now - timedelta(
            minutes=15
        )  # Success after error

        result = FeedDomain.calculate_feed_status(feed)

        # Success is most recent, so status is healthy
        assert result == "healthy"

    def test_status_error_when_error_after_success_within_hour(self):
        """Should return 'error' when error is after success."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        # Error after success, but still recent
        now = datetime.now(UTC)
        feed.last_fetched_at = now - timedelta(minutes=45)
        feed.last_error_at = now - timedelta(minutes=30)

        result = FeedDomain.calculate_feed_status(feed)

        # Error is after success, so status is error
        assert result == "error"

    def test_status_healthy_when_exactly_hour(self):
        """Should return 'stale' when exactly 1 hour since last success."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        feed.last_error_at = None
        feed.last_fetched_at = datetime.now(UTC) - timedelta(hours=1)

        result = FeedDomain.calculate_feed_status(feed)

        assert result == "stale"

    def test_status_healthy_when_under_hour(self):
        """Should return 'healthy' when under 1 hour since last success."""
        from unittest.mock import MagicMock

        feed = MagicMock()
        feed.last_error_at = None
        feed.last_fetched_at = datetime.now(UTC) - timedelta(minutes=59)

        result = FeedDomain.calculate_feed_status(feed)

        assert result == "healthy"

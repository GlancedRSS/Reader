"""Unit tests for FeedDomain."""

from datetime import UTC, datetime, timedelta

from backend.domain.feed.feed import FeedDomain


class TestFeedDomainStatus:
    """Test feed status calculation."""

    def test_calculate_feed_status_with_none_feed(self):
        """Should return 'error' when feed is None."""
        status = FeedDomain.calculate_feed_status(None)
        assert status == "error"

    def test_calculate_feed_status_healthy_when_recently_fetched(self):
        """Should return 'healthy' when feed was recently fetched."""
        now = datetime.now(UTC)
        feed = MockFeed(
            last_fetched_at=now - timedelta(minutes=30),
            last_error_at=None,
        )
        status = FeedDomain.calculate_feed_status(feed)
        assert status == "healthy"

    def test_calculate_feed_status_stale_when_fetched_long_ago(self):
        """Should return 'stale' when feed was fetched over 1 hour ago."""
        old_time = datetime.now(UTC) - timedelta(hours=2)
        feed = MockFeed(
            last_fetched_at=old_time,
            last_error_at=None,
        )
        status = FeedDomain.calculate_feed_status(feed)
        assert status == "stale"

    def test_calculate_feed_status_stale_when_never_fetched(self):
        """Should return 'stale' when feed was never fetched."""
        feed = MockFeed(
            last_fetched_at=None,
            last_error_at=None,
        )
        status = FeedDomain.calculate_feed_status(feed)
        assert status == "stale"

    def test_calculate_feed_status_error_when_error_after_fetch(self):
        """Should return 'error' when last error occurred after last fetch."""
        now = datetime.now(UTC)
        feed = MockFeed(
            last_fetched_at=now - timedelta(hours=2),
            last_error_at=now - timedelta(minutes=30),
        )
        status = FeedDomain.calculate_feed_status(feed)
        assert status == "error"

    def test_calculate_feed_status_healthy_when_error_before_fetch(self):
        """Should return 'healthy' when last error was before last fetch."""
        now = datetime.now(UTC)
        feed = MockFeed(
            last_fetched_at=now - timedelta(minutes=30),
            last_error_at=now - timedelta(hours=2),
        )
        status = FeedDomain.calculate_feed_status(feed)
        assert status == "healthy"

    def test_calculate_feed_status_error_when_error_exists_no_fetch(self):
        """Should return 'error' when error exists but no successful fetch."""
        feed = MockFeed(
            last_fetched_at=None,
            last_error_at=datetime.now(UTC) - timedelta(minutes=10),
        )
        status = FeedDomain.calculate_feed_status(feed)
        assert status == "error"


class MockFeed:
    """Mock feed object for testing."""

    def __init__(self, last_fetched_at, last_error_at):
        self.last_fetched_at = last_fetched_at
        self.last_error_at = last_error_at

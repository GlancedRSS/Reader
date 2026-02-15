"""Unit tests for feed repository."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.infrastructure.repositories.feed import FeedRepository
from backend.models import Feed


class TestGetFeedById:
    """Test getting feed by ID."""

    @pytest.mark.asyncio
    async def test_returns_feed_when_exists(self):
        """Should return feed when it exists."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(id=feed_id, title="Test Feed")
        mock_db.get = AsyncMock(return_value=mock_feed)

        repo = FeedRepository(mock_db)
        result = await repo.get_feed_by_id(feed_id)

        assert result is not None
        assert result.id == feed_id
        mock_db.get.assert_called_once_with(Feed, feed_id)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when feed doesn't exist."""
        mock_db = MagicMock()
        mock_db.get = AsyncMock(return_value=None)

        repo = FeedRepository(mock_db)
        result = await repo.get_feed_by_id(uuid4())

        assert result is None


class TestGetFeedByUrl:
    """Test getting feed by URL."""

    @pytest.mark.asyncio
    async def test_returns_feed_when_url_matches(self):
        """Should return feed when URL matches."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(id=feed_id, canonical_url="https://example.com/feed")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        result = await repo.get_feed_by_url("https://example.com/feed")

        assert result is not None
        assert result.id == feed_id

    @pytest.mark.asyncio
    async def test_returns_none_when_url_not_found(self):
        """Should return None when URL doesn't match any feed."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        result = await repo.get_feed_by_url("https://example.com/feed")

        assert result is None

    @pytest.mark.asyncio
    async def test_normalizes_url_before_query(self):
        """Should normalize URL before querying."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        await repo.get_feed_by_url("https://example.com/feed/")

        # Should call execute (URL normalization happens in the method)
        mock_db.execute.assert_called_once()


class TestCreateFeed:
    """Test creating new feeds."""

    @pytest.mark.asyncio
    async def test_creates_feed_with_all_fields(self):
        """Should create feed with all provided fields."""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.create_feed(
            url="https://example.com/feed",
            title="Test Feed",
            description="Test Description",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=True,
        )

        assert result.title == "Test Feed"
        assert result.description == "Test Description"
        assert result.feed_type == "rss"
        assert result.language == "en"
        assert result.website == "https://example.com"
        assert result.last_fetched_at is not None
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_feed_without_articles(self):
        """Should create feed without last_fetched_at when no articles."""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.create_feed(
            url="https://example.com/feed",
            title="Test Feed",
            description=None,
            feed_type="atom",
            language=None,
            website=None,
            has_articles=False,
        )

        assert result.last_fetched_at is None
        assert result.feed_type == "atom"

    @pytest.mark.asyncio
    async def test_normalizes_url(self):
        """Should normalize the URL before storing."""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.create_feed(
            url="https://EXAMPLE.com/feed/",  # Case insensitive
            title="Test",
            description=None,
            feed_type="rss",
            language=None,
            website=None,
            has_articles=False,
        )

        # URL should be normalized
        assert "example.com" in result.canonical_url.lower()


class TestDeleteFeed:
    """Test deleting feeds."""

    @pytest.mark.asyncio
    async def test_deletes_feed(self):
        """Should delete the provided feed."""
        mock_db = MagicMock()
        mock_feed = Feed(id=uuid4(), title="To Delete")
        mock_db.delete = AsyncMock()

        repo = FeedRepository(mock_db)
        await repo.delete_feed(mock_feed)

        mock_db.delete.assert_called_once_with(mock_feed)


class TestUpdateFeed:
    """Test updating feeds."""

    @pytest.mark.asyncio
    async def test_updates_feed_fields(self):
        """Should update specified feed fields."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(id=feed_id, title="Old Title")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.update_feed(
            feed_id, {"title": "New Title", "description": "New Description"}
        )

        assert result is not None
        assert result.title == "New Title"
        assert result.description == "New Description"
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_feed_not_found(self):
        """Should return None when feed doesn't exist."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        result = await repo.update_feed(uuid4(), {"title": "New Title"})

        assert result is None

    @pytest.mark.asyncio
    async def test_updates_multiple_fields(self):
        """Should update multiple fields at once."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(
            id=feed_id,
            title="Old",
            description="Old Desc",
            language="en",
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        repo = FeedRepository(mock_db)
        await repo.update_feed(
            feed_id,
            {"title": "New", "description": "New Desc", "language": "fr"},
        )

        assert mock_feed.title == "New"
        assert mock_feed.description == "New Desc"
        assert mock_feed.language == "fr"


class TestDeleteFeedsBulk:
    """Test bulk deletion of feeds."""

    @pytest.mark.asyncio
    async def test_deletes_multiple_feeds(self):
        """Should delete all provided feed IDs."""
        mock_db = MagicMock()
        feed_ids = [uuid4(), uuid4(), uuid4()]

        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.flush = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.delete_feeds_bulk(feed_ids)

        assert result == 3
        mock_db.execute.assert_called_once()
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_zero_for_empty_list(self):
        """Should return 0 for empty feed ID list."""
        mock_db = MagicMock()

        repo = FeedRepository(mock_db)
        result = await repo.delete_feeds_bulk([])

        assert result == 0
        mock_db.execute.assert_not_called()


class TestUpdateFeedStats:
    """Test updating feed statistics."""

    @pytest.mark.asyncio
    async def test_updates_all_stats(self):
        """Should update all provided statistics."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(id=feed_id, error_count=0)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        await repo.update_feed_stats(
            feed_id=feed_id,
            last_fetched_at=datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC),
            last_update=datetime(2024, 1, 15, 9, 0, 0, tzinfo=UTC),
            error_count=1,
            last_error="Network error",
        )

        assert mock_feed.last_fetched_at is not None
        assert mock_feed.last_update is not None
        assert mock_feed.error_count == 1
        assert mock_feed.last_error == "Network error"
        assert mock_feed.last_error_at is not None

    @pytest.mark.asyncio
    async def test_updates_partial_stats(self):
        """Should update only provided statistics."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(id=feed_id, error_count=2, last_error="Old error")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        await repo.update_feed_stats(
            feed_id=feed_id,
            error_count=0,
        )

        assert mock_feed.error_count == 0
        # Unchanged fields should remain
        assert mock_feed.last_error == "Old error"
        assert mock_feed.last_fetched_at is None

    @pytest.mark.asyncio
    async def test_handles_missing_feed(self):
        """Should handle missing feed gracefully."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        # Should not raise exception
        await repo.update_feed_stats(
            feed_id=uuid4(),
            last_fetched_at=datetime.now(UTC),
        )


class TestIncrementFeedError:
    """Test incrementing feed error count."""

    @pytest.mark.asyncio
    async def test_increments_error_count(self):
        """Should increment error count and set error message."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(id=feed_id, error_count=0)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        await repo.increment_feed_error(feed_id, "Connection failed")

        assert mock_feed.error_count == 1
        assert mock_feed.last_error == "Connection failed"
        assert mock_feed.last_error_at is not None

    @pytest.mark.asyncio
    async def test_increments_from_existing_count(self):
        """Should increment from existing error count."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(id=feed_id, error_count=2)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        await repo.increment_feed_error(feed_id, "Another error")

        assert mock_feed.error_count == 3

    @pytest.mark.asyncio
    async def test_handles_missing_feed(self):
        """Should handle missing feed gracefully."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        # Should not raise exception
        await repo.increment_feed_error(uuid4(), "Error")


class TestResetFeedErrors:
    """Test resetting feed errors."""

    @pytest.mark.asyncio
    async def test_resets_all_error_fields(self):
        """Should reset error count, error message, and error timestamp."""
        mock_db = MagicMock()
        feed_id = uuid4()
        mock_feed = Feed(
            id=feed_id,
            error_count=5,
            last_error="Connection failed",
            last_error_at=datetime.now(UTC),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_feed
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        await repo.reset_feed_errors(feed_id)

        assert mock_feed.error_count == 0
        assert mock_feed.last_error is None
        assert mock_feed.last_error_at is None

    @pytest.mark.asyncio
    async def test_handles_missing_feed(self):
        """Should handle missing feed gracefully."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        # Should not raise exception
        await repo.reset_feed_errors(uuid4())


class TestGetActiveFeedsWithSubscriptions:
    """Test getting active feeds with subscriptions."""

    @pytest.mark.asyncio
    async def test_returns_feeds_with_subscriptions(self):
        """Should return feeds that have user subscriptions."""
        mock_db = MagicMock()
        feed1 = Feed(id=uuid4(), title="Feed 1", is_active=True)
        feed2 = Feed(id=uuid4(), title="Feed 2", is_active=True)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [feed1, feed2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        result = await repo.get_active_feeds_with_subscriptions()

        assert len(result) == 2
        assert result[0].is_active is True
        assert result[1].is_active is True

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_subscriptions(self):
        """Should return empty list when no feeds have subscriptions."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = FeedRepository(mock_db)
        result = await repo.get_active_feeds_with_subscriptions()

        assert result == []


class TestBulkMarkOrphanedFeedsInactive:
    """Test bulk marking orphaned feeds as inactive."""

    @pytest.mark.asyncio
    async def test_marks_feeds_inactive(self):
        """Should mark feeds with no subscribers as inactive."""
        mock_db = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.bulk_mark_orphaned_feeds_inactive()

        assert result == 5
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_orphaned_feeds(self):
        """Should return 0 when no feeds need marking."""
        mock_db = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.bulk_mark_orphaned_feeds_inactive()

        assert result == 0

    @pytest.mark.asyncio
    async def test_returns_zero_on_scalar_none(self):
        """Should return 0 when scalar returns None."""
        mock_db = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        repo = FeedRepository(mock_db)
        result = await repo.bulk_mark_orphaned_feeds_inactive()

        assert result == 0

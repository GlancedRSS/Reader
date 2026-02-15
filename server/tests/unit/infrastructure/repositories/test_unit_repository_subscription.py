"""Unit tests for subscription repository."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.infrastructure.repositories.subscription import (
    SubscriptionRepository,
)


class TestGetArticlesForFeed:
    """Test getting articles for a feed."""

    @pytest.mark.asyncio
    async def test_returns_articles_for_feed(self):
        """Should return articles associated with a feed."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            "article1",
            "article2",
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_articles_for_feed(uuid4())

        assert len(result) == 2
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_feed_with_no_articles(self):
        """Should return empty list when feed has no articles."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_articles_for_feed(uuid4())

        assert result == []


class TestGetArticleIdsForFeed:
    """Test getting article IDs for a feed."""

    @pytest.mark.asyncio
    async def test_returns_article_ids(self):
        """Should return article IDs for a feed."""
        mock_db = MagicMock()
        article_ids = [uuid4(), uuid4(), uuid4()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = article_ids
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_article_ids_for_feed(uuid4())

        assert len(result) == 3
        assert result == article_ids

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_articles(self):
        """Should return empty list when no articles found."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_article_ids_for_feed(uuid4())

        assert result == []


class TestGetRecentArticleIdsForFeed:
    """Test getting recent article IDs from feed's latest_articles array."""

    @pytest.mark.asyncio
    async def test_returns_latest_articles_from_feed(self):
        """Should return article IDs from feed's latest_articles array."""
        mock_db = MagicMock()
        feed_id = uuid4()
        article_ids = [uuid4(), uuid4()]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = article_ids
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_recent_article_ids_for_feed(
            feed_id, datetime.now(UTC)
        )

        assert result == article_ids

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_feed_has_no_latest_articles(self):
        """Should return empty list when feed has no latest_articles."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_recent_article_ids_for_feed(
            uuid4(), datetime.now(UTC)
        )

        assert result == []


class TestBulkUpsertUserArticleStates:
    """Test bulk upsert of user article states."""

    @pytest.mark.asyncio
    async def test_returns_zero_for_empty_article_list(self):
        """Should return 0 when no article IDs provided."""
        mock_db = MagicMock()

        repo = SubscriptionRepository(mock_db)
        result = await repo.bulk_upsert_user_article_states(uuid4(), [])

        assert result == 0
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_rowcount_on_success(self):
        """Should return rowcount on successful insert."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.bulk_upsert_user_article_states(
            uuid4(), [uuid4(), uuid4()]
        )

        assert result == 5
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_zero_when_result_has_no_rowcount(self):
        """Should return 0 when result has no rowcount attribute."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        # Remove rowcount attribute
        del mock_result.rowcount
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.bulk_upsert_user_article_states(uuid4(), [uuid4()])

        assert result == 0


class TestRecalculateSubscriptionUnreadCount:
    """Test recalculation of subscription unread count."""

    @pytest.mark.asyncio
    async def test_returns_count_on_success(self):
        """Should return recalculated count."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.recalculate_subscription_unread_count(uuid4())

        assert result == 42

    @pytest.mark.asyncio
    async def test_returns_none_on_error(self):
        """Should return None when query fails."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(side_effect=Exception("DB error"))

        repo = SubscriptionRepository(mock_db)
        result = await repo.recalculate_subscription_unread_count(uuid4())

        assert result is None


class TestCreateArticleTagRelationship:
    """Test creating article-tag relationship."""

    @pytest.mark.asyncio
    async def test_delegates_to_tag_repository(self):
        """Should delegate to tag repository."""
        mock_db = MagicMock()
        mock_tag_repo = MagicMock()
        mock_tag_repo.add_tags_to_article = AsyncMock()

        repo = SubscriptionRepository(mock_db)
        repo.tag_repository = mock_tag_repo

        await repo.create_article_tag_relationship(uuid4(), uuid4(), uuid4())

        mock_tag_repo.add_tags_to_article.assert_called_once()


class TestGetUnreadArticlesForUser:
    """Test getting unread articles for a user."""

    @pytest.mark.asyncio
    async def test_returns_unread_articles(self):
        """Should return unread articles older than cutoff date."""
        mock_db = MagicMock()
        mock_ua1 = MagicMock()
        mock_ua2 = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_ua1, mock_ua2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_unread_articles_for_user(
            uuid4(), datetime.now(UTC)
        )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_unread_articles(self):
        """Should return empty list when no unread articles found."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.get_unread_articles_for_user(
            uuid4(), datetime.now(UTC)
        )

        assert result == []


class TestMarkArticlesAsRead:
    """Test marking articles as read."""

    @pytest.mark.asyncio
    async def test_returns_zero_for_empty_article_list(self):
        """Should return 0 when no article IDs provided."""
        mock_db = MagicMock()

        repo = SubscriptionRepository(mock_db)
        result = await repo.mark_articles_as_read(uuid4(), [])

        assert result == 0

    @pytest.mark.asyncio
    async def test_marks_articles_as_read(self):
        """Should mark provided articles as read."""
        mock_db = MagicMock()
        mock_ua1 = MagicMock()
        mock_ua2 = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_ua1, mock_ua2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        result = await repo.mark_articles_as_read(uuid4(), [uuid4(), uuid4()])

        assert result == 2
        assert mock_ua1.is_read is True
        assert mock_ua2.is_read is True
        assert mock_ua1.read_at is not None
        assert mock_ua2.read_at is not None

    @pytest.mark.asyncio
    async def test_uses_provided_read_at_timestamp(self):
        """Should use provided read_at timestamp."""
        mock_db = MagicMock()
        mock_ua = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_ua]
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = SubscriptionRepository(mock_db)
        read_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        await repo.mark_articles_as_read(uuid4(), [uuid4()], read_at=read_at)

        assert mock_ua.read_at == read_at


class TestBulkMarkOldArticlesAsRead:
    """Test bulk marking old articles as read."""

    @pytest.mark.asyncio
    async def test_executes_bulk_update_query(self):
        """Should execute bulk update query with correct cutoff dates."""
        mock_db = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: {0: 5, 1: 100}.get(key)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        repo = SubscriptionRepository(mock_db)
        cutoff_7 = datetime.now(UTC)
        cutoff_14 = datetime.now(UTC)
        cutoff_30 = datetime.now(UTC)

        result = await repo.bulk_mark_old_articles_as_read(
            cutoff_date_7days=cutoff_7,
            cutoff_date_14days=cutoff_14,
            cutoff_date_30days=cutoff_30,
        )

        assert result["users_affected"] == 5
        assert result["articles_marked"] == 100
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_defaults_read_at_to_now(self):
        """Should default read_at to current time."""
        mock_db = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: {0: 1, 1: 10}.get(key)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_row
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        repo = SubscriptionRepository(mock_db)

        await repo.bulk_mark_old_articles_as_read(
            cutoff_date_7days=datetime.now(UTC),
            cutoff_date_14days=datetime.now(UTC),
            cutoff_date_30days=datetime.now(UTC),
        )

        # Verify read_at was passed (second positional arg is the params dict)
        call_args = mock_db.execute.call_args
        params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert "read_at" in params
        assert isinstance(params["read_at"], datetime)

    @pytest.mark.asyncio
    async def test_handles_empty_result(self):
        """Should handle empty query result."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        repo = SubscriptionRepository(mock_db)

        result = await repo.bulk_mark_old_articles_as_read(
            cutoff_date_7days=datetime.now(UTC),
            cutoff_date_14days=datetime.now(UTC),
            cutoff_date_30days=datetime.now(UTC),
        )

        assert result["users_affected"] == 0
        assert result["articles_marked"] == 0

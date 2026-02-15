"""Unit tests for FeedApplication."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.feed import FeedApplication
from backend.core.exceptions import NotFoundError, ValidationError
from backend.schemas.domain import (
    UserFeedUpdateRequest,
)


class TestFeedApplicationGetUserFeedsPaginated:
    """Test get user feeds with pagination."""

    @pytest.mark.asyncio
    async def test_get_user_feeds_paginated_returns_feeds(
        self, db_session: AsyncSession
    ):
        """Should return paginated user feeds."""
        user_id = uuid4()

        mock_feed = MagicMock()
        mock_feed.last_error_at = None
        mock_feed.last_fetched_at = datetime.now(UTC)

        mock_subscription = MagicMock()
        mock_subscription.id = uuid4()
        mock_subscription.title = "Test Feed"
        mock_subscription.unread_count = 5
        mock_subscription.is_pinned = True
        mock_subscription.is_active = True
        mock_subscription.feed = mock_feed
        mock_subscription.feed.website = "https://example.com"

        mock_repo = MagicMock()
        mock_repo.get_user_feeds_paginated = AsyncMock(
            return_value=[mock_subscription]
        )
        mock_repo.get_user_feeds_count = AsyncMock(return_value=1)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        response = await app.get_user_feeds_paginated(user_id)

        assert len(response.data) == 1
        assert response.data[0].title == "Test Feed"
        assert response.pagination.total == 1

    @pytest.mark.asyncio
    async def test_get_user_feeds_paginated_with_cursor_based_pagination(
        self, db_session: AsyncSession
    ):
        """Should use cursor-based pagination when order_by='recent'."""
        user_id = uuid4()

        mock_query_result = MagicMock()
        mock_query_result.user_feeds = []
        mock_query_result.has_more = False
        mock_query_result.next_cursor = "next_cursor"

        mock_repo = MagicMock()
        mock_repo.get_user_feeds_paginated_cursor = AsyncMock(
            return_value=mock_query_result
        )
        mock_repo.get_user_feeds_count = AsyncMock(return_value=0)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        response = await app.get_user_feeds_paginated(
            user_id, order_by="recent"
        )

        mock_repo.get_user_feeds_paginated_cursor.assert_called_once()
        assert response.pagination.next_cursor == "next_cursor"

    @pytest.mark.asyncio
    async def test_get_user_feeds_paginated_with_name_ordering(
        self, db_session: AsyncSession
    ):
        """Should sort by name alphabetically when order_by='name'."""
        user_id = uuid4()

        mock_feed = MagicMock()
        mock_feed.last_error_at = None
        mock_feed.last_fetched_at = datetime.now(UTC)

        mock_sub1 = MagicMock()
        mock_sub1.id = uuid4()
        mock_sub1.title = "Zebra Feed"
        mock_sub1.feed = mock_feed
        mock_sub1.feed.website = "https://example.com"
        mock_sub1.unread_count = 0
        mock_sub1.is_pinned = False
        mock_sub1.is_active = True

        mock_sub2 = MagicMock()
        mock_sub2.id = uuid4()
        mock_sub2.title = "Apple Feed"
        mock_sub2.feed = mock_feed
        mock_sub2.feed.website = "https://example.com"
        mock_sub2.unread_count = 0
        mock_sub2.is_pinned = False
        mock_sub2.is_active = True

        mock_repo = MagicMock()
        mock_repo.get_user_feeds_paginated = AsyncMock(
            return_value=[mock_sub1, mock_sub2]
        )
        mock_repo.get_user_feeds_count = AsyncMock(return_value=2)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        response = await app.get_user_feeds_paginated(user_id, order_by="name")

        # Should be sorted alphabetically
        assert response.data[0].title == "Apple Feed"
        assert response.data[1].title == "Zebra Feed"


class TestFeedApplicationGetUserFeedById:
    """Test get user feed by ID."""

    @pytest.mark.asyncio
    async def test_get_user_feed_by_id_returns_feed_details(
        self, db_session: AsyncSession
    ):
        """Should return detailed user feed information."""
        user_feed_id = uuid4()
        user_id = uuid4()
        folder_id = uuid4()

        mock_feed = MagicMock()
        mock_feed.description = "Test description"
        mock_feed.website = "https://example.com"
        mock_feed.language = "en"
        mock_feed.last_update = "2024-01-01T00:00:00Z"
        mock_feed.canonical_url = "https://example.com/feed"
        mock_feed.last_error_at = None
        mock_feed.last_fetched_at = datetime.now(UTC)

        mock_user_feed = MagicMock()
        mock_user_feed.id = user_feed_id
        mock_user_feed.user_id = user_id
        mock_user_feed.title = "Test Feed"
        mock_user_feed.unread_count = 10
        mock_user_feed.is_pinned = True
        mock_user_feed.is_active = True
        mock_user_feed.folder_id = folder_id
        mock_user_feed.feed = mock_feed

        mock_folder = MagicMock()
        mock_folder.name = "Test Folder"
        mock_user_feed.folder = mock_folder

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=mock_user_feed)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        response = await app.get_user_feed_by_id(user_feed_id, user_id)

        assert response.title == "Test Feed"
        assert response.unread_count == 10
        assert response.folder_name == "Test Folder"

    @pytest.mark.asyncio
    async def test_get_user_feed_by_id_raises_not_found_when_not_exists(
        self, db_session: AsyncSession
    ):
        """Should raise NotFoundError when user feed doesn't exist."""
        user_feed_id = uuid4()
        user_id = uuid4()

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=None)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(NotFoundError) as exc_info:
            await app.get_user_feed_by_id(user_feed_id, user_id)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_user_feed_by_id_raises_not_found_when_user_mismatch(
        self, db_session: AsyncSession
    ):
        """Should raise NotFoundError when user doesn't own the feed."""
        user_feed_id = uuid4()
        user_id = uuid4()
        other_user_id = uuid4()

        mock_user_feed = MagicMock()
        mock_user_feed.user_id = other_user_id

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=mock_user_feed)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(NotFoundError) as exc_info:
            await app.get_user_feed_by_id(user_feed_id, user_id)

        assert "not found" in str(exc_info.value).lower()


class TestFeedApplicationUpdateUserFeed:
    """Test update user feed operations."""

    @pytest.mark.asyncio
    async def test_update_user_feed_updates_title(
        self, db_session: AsyncSession
    ):
        """Should update user feed title."""
        user_feed_id = uuid4()
        user_id = uuid4()

        mock_user_feed = MagicMock()
        mock_user_feed.user_id = user_id
        mock_user_feed.title = "Old Title"
        mock_user_feed.is_active = True

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=mock_user_feed)
        mock_repo.update_user_feed = AsyncMock()

        app = FeedApplication(db_session)
        app.repository = mock_repo

        request = UserFeedUpdateRequest(title="New Title")
        response = await app.update_user_feed(user_feed_id, request, user_id)

        assert "updated successfully" in response.message.lower()
        mock_repo.update_user_feed.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_feed_with_invalid_folder_raises_validation_error(
        self, db_session: AsyncSession
    ):
        """Should raise ValidationError when folder_id is invalid."""
        user_feed_id = uuid4()
        user_id = uuid4()
        folder_id = uuid4()

        mock_user_feed = MagicMock()
        mock_user_feed.user_id = user_id

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=mock_user_feed)
        mock_repo.validate_folder_for_user = AsyncMock(return_value=None)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        request = UserFeedUpdateRequest(folder_id=folder_id)

        with pytest.raises(ValidationError) as exc_info:
            await app.update_user_feed(user_feed_id, request, user_id)

        assert "invalid folder" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_user_feed_raises_not_found_when_not_exists(
        self, db_session: AsyncSession
    ):
        """Should raise NotFoundError when user feed doesn't exist."""
        user_feed_id = uuid4()
        user_id = uuid4()

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=None)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        request = UserFeedUpdateRequest(title="New Title")

        with pytest.raises(NotFoundError) as exc_info:
            await app.update_user_feed(user_feed_id, request, user_id)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_user_feed_handles_resume_with_backfill(
        self, db_session: AsyncSession
    ):
        """Should backfill articles when resuming a paused feed."""
        user_feed_id = uuid4()
        user_id = uuid4()
        feed_id = uuid4()

        mock_user_feed = MagicMock()
        mock_user_feed.user_id = user_id
        mock_user_feed.is_active = False
        mock_user_feed.feed_id = feed_id

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=mock_user_feed)
        mock_repo.update_user_feed = AsyncMock()
        mock_repo.get_recent_article_ids_for_feed = AsyncMock(
            return_value=[uuid4()]
        )
        mock_repo.bulk_upsert_user_article_states = AsyncMock(return_value=1)

        app = FeedApplication(db_session)
        app.repository = mock_repo
        app._backfill_tags_for_articles = AsyncMock(return_value=1)

        request = UserFeedUpdateRequest(is_active=True)
        response = await app.update_user_feed(user_feed_id, request, user_id)

        assert "updated successfully" in response.message.lower()
        mock_repo.bulk_upsert_user_article_states.assert_called_once()


class TestFeedApplicationUnsubscribeFromFeed:
    """Test unsubscribe from feed operations."""

    @pytest.mark.asyncio
    async def test_unsubscribe_from_feed_deletes_subscription(
        self, db_session: AsyncSession
    ):
        """Should delete user feed and associated articles."""
        user_feed_id = uuid4()
        user_id = uuid4()
        feed_id = uuid4()

        mock_user_feed = MagicMock()
        mock_user_feed.user_id = user_id
        mock_user_feed.feed_id = feed_id

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=mock_user_feed)
        mock_repo.get_article_ids_for_feed = AsyncMock(return_value=[uuid4()])
        mock_repo.get_article_ids_accessible_via_other_feeds = AsyncMock(
            return_value=[]
        )
        mock_repo.delete_user_articles = AsyncMock(return_value=1)
        mock_repo.delete_user_feed = AsyncMock()

        mock_tag_repo = MagicMock()
        mock_tag_repo.remove_articles_from_all_tags = AsyncMock()

        app = FeedApplication(db_session)
        app.repository = mock_repo
        app.tag_repository = mock_tag_repo

        response = await app.unsubscribe_from_feed(user_feed_id, user_id)

        assert "successfully unsubscribed" in response.message.lower()
        mock_repo.delete_user_feed.assert_called_once_with(mock_user_feed)

    @pytest.mark.asyncio
    async def test_unsubscribe_from_feed_raises_not_found_when_not_exists(
        self, db_session: AsyncSession
    ):
        """Should raise NotFoundError when user feed doesn't exist."""
        user_feed_id = uuid4()
        user_id = uuid4()

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=None)

        app = FeedApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(NotFoundError) as exc_info:
            await app.unsubscribe_from_feed(user_feed_id, user_id)

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_unsubscribe_from_feed_preserves_shared_articles(
        self, db_session: AsyncSession
    ):
        """Should not delete articles accessible via other feeds."""
        user_feed_id = uuid4()
        user_id = uuid4()
        feed_id = uuid4()
        article_id = uuid4()

        mock_user_feed = MagicMock()
        mock_user_feed.user_id = user_id
        mock_user_feed.feed_id = feed_id

        mock_repo = MagicMock()
        mock_repo.get_user_feed_by_id = AsyncMock(return_value=mock_user_feed)
        mock_repo.get_article_ids_for_feed = AsyncMock(
            return_value=[article_id]
        )
        # Article is accessible via other feeds
        mock_repo.get_article_ids_accessible_via_other_feeds = AsyncMock(
            return_value=[article_id]
        )
        mock_repo.delete_user_feed = AsyncMock()

        app = FeedApplication(db_session)
        app.repository = mock_repo

        response = await app.unsubscribe_from_feed(user_feed_id, user_id)

        # delete_user_articles should NOT be called since article is accessible elsewhere
        mock_repo.delete_user_articles.assert_not_called()
        assert "successfully unsubscribed" in response.message.lower()


class TestFeedApplicationBackfillTagsForArticles:
    """Test backfill tags for articles operations."""

    @pytest.mark.asyncio
    async def test_backfill_tags_creates_article_tags(
        self, db_session: AsyncSession
    ):
        """Should create ArticleTag records for articles with source_tags."""
        user_id = uuid4()
        article_id = uuid4()
        tag_id = uuid4()
        user_article_id = uuid4()

        mock_article = MagicMock()
        mock_article.id = article_id
        mock_article.source_tags = ["tech", "news"]

        mock_user_article = MagicMock()
        mock_user_article.id = user_article_id
        mock_user_article.article_id = article_id

        mock_tag = MagicMock()
        mock_tag.id = tag_id

        # First call: get articles, Second call: get user_articles
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[mock_article])
        mock_scalars2 = MagicMock()
        mock_scalars2.all = MagicMock(return_value=[mock_user_article])

        mock_execute_result = MagicMock()
        mock_execute_result.scalars = MagicMock(return_value=mock_scalars)
        mock_execute_result2 = MagicMock()
        mock_execute_result2.scalars = MagicMock(return_value=mock_scalars2)
        # Third call: get existing tag pairs - return empty
        mock_execute_result3 = MagicMock()
        mock_execute_result3.all = MagicMock(return_value=[])

        db_session.execute = AsyncMock(
            side_effect=[
                mock_execute_result,
                mock_execute_result2,
                mock_execute_result3,
            ]
        )
        db_session.flush = AsyncMock()

        mock_tag_repo = MagicMock()
        mock_tag_repo.get_or_create_tag = AsyncMock(return_value=mock_tag)

        app = FeedApplication(db_session)
        app.tag_repository = mock_tag_repo

        result = await app._backfill_tags_for_articles(user_id, [article_id])

        assert result > 0

    @pytest.mark.asyncio
    async def test_backfill_tags_returns_zero_for_empty_list(
        self, db_session: AsyncSession
    ):
        """Should return 0 when article_ids is empty."""
        user_id = uuid4()

        app = FeedApplication(db_session)

        result = await app._backfill_tags_for_articles(user_id, [])

        assert result == 0

    @pytest.mark.asyncio
    async def test_backfill_tags_skips_existing_tags(
        self, db_session: AsyncSession
    ):
        """Should skip creating tags that already exist."""
        user_id = uuid4()
        article_id = uuid4()
        tag_id = uuid4()
        user_article_id = uuid4()

        mock_article = MagicMock()
        mock_article.id = article_id
        mock_article.source_tags = ["tech"]

        mock_user_article = MagicMock()
        mock_user_article.id = user_article_id
        mock_user_article.article_id = article_id

        mock_tag = MagicMock()
        mock_tag.id = tag_id

        # Simulate existing tag pair
        mock_row = MagicMock()
        mock_row.user_article_id = user_article_id
        mock_row.user_tag_id = tag_id

        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[mock_article])
        mock_scalars2 = MagicMock()
        mock_scalars2.all = MagicMock(return_value=[mock_user_article])

        mock_execute_result = MagicMock()
        mock_execute_result.scalars = MagicMock(return_value=mock_scalars)
        mock_execute_result2 = MagicMock()
        mock_execute_result2.scalars = MagicMock(return_value=mock_scalars2)
        # Third call: get existing tag pairs - return existing pair
        mock_execute_result3 = MagicMock()
        mock_execute_result3.all = MagicMock(return_value=[mock_row])

        db_session.execute = AsyncMock(
            side_effect=[
                mock_execute_result,
                mock_execute_result2,
                mock_execute_result3,
            ]
        )
        db_session.flush = AsyncMock()

        mock_tag_repo = MagicMock()
        mock_tag_repo.get_or_create_tag = AsyncMock(return_value=mock_tag)

        app = FeedApplication(db_session)
        app.tag_repository = mock_tag_repo

        result = await app._backfill_tags_for_articles(user_id, [article_id])

        # Should return 0 since tag already exists
        assert result == 0

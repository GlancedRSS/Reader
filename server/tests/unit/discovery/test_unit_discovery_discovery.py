"""Unit tests for DiscoveryApplication."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.application.discovery.discovery import DiscoveryApplication
from backend.models.user_feed import UserFeed

if TYPE_CHECKING:
    pass


class TestDiscoverFeedsExistingFeedSubscribed:
    """Test discover_feeds when feed exists globally and user is already subscribed."""

    @pytest.mark.asyncio
    async def test_existing_subscription_no_folder_change(self, db_session):
        """Should return 'existing' status when user already subscribed without folder change."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=None,
        )
        existing_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=None,
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = (
            existing_subscription
        )
        mock_folder_repo = AsyncMock()
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "existing"
        assert result.message == "Already subscribed"
        mock_user_feed_repo.update_user_feed.assert_not_called()

    @pytest.mark.asyncio
    async def test_existing_subscription_with_valid_folder_move(
        self, db_session
    ):
        """Should return 'moved' status when moving subscription to valid folder."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        folder_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=None,
        )
        existing_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=None,
        )
        valid_folder = MagicMock(id=folder_id, name="Tech")

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = (
            existing_subscription
        )
        mock_folder_repo = AsyncMock()
        mock_folder_repo.find_by_id.return_value = valid_folder
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=folder_id
        )

        # Assert
        assert result.status == "moved"
        assert result.message == "Feed moved"
        mock_user_feed_repo.update_user_feed.assert_called_once_with(
            existing_subscription, {"folder_id": folder_id}
        )

    @pytest.mark.asyncio
    async def test_existing_subscription_with_invalid_folder(self, db_session):
        """Should return 'existing' with folder warning when folder not found."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        folder_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=None,
        )
        existing_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=None,
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = (
            existing_subscription
        )
        mock_folder_repo = AsyncMock()
        mock_folder_repo.find_by_id.return_value = None
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=folder_id
        )

        # Assert
        assert result.status == "existing"
        assert "Folder not found" in result.message
        mock_user_feed_repo.update_user_feed.assert_not_called()


class TestDiscoverFeedsExistingFeedNotSubscribed:
    """Test discover_feeds when feed exists globally but user is not subscribed."""

    @pytest.mark.asyncio
    async def test_subscribe_to_existing_feed_without_folder(self, db_session):
        """Should subscribe successfully and return 'subscribed' status."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        article_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=[article_id],
        )
        new_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=None,
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = None
        mock_user_feed_repo.create_user_feed.return_value = new_subscription
        mock_user_feed_repo.bulk_upsert_user_article_states.return_value = 1
        mock_folder_repo = AsyncMock()
        mock_feed_app = AsyncMock()
        mock_feed_app._backfill_tags_for_articles.return_value = 0
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=mock_feed_app,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "subscribed"
        assert result.message == "Subscribed successfully"
        mock_user_feed_repo.create_user_feed.assert_called_once()
        mock_user_feed_repo.bulk_upsert_user_article_states.assert_called_once_with(
            user_id, [article_id]
        )
        mock_feed_app._backfill_tags_for_articles.assert_called_once_with(
            user_id, [article_id]
        )

    @pytest.mark.asyncio
    async def test_subscribe_to_existing_feed_with_valid_folder(
        self, db_session
    ):
        """Should subscribe to folder when folder_id is valid."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        folder_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=[],
        )
        new_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=folder_id,
        )
        valid_folder = MagicMock(id=folder_id, name="Tech")

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = None
        mock_user_feed_repo.create_user_feed.return_value = new_subscription
        mock_folder_repo = AsyncMock()
        mock_folder_repo.find_by_id.return_value = valid_folder
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=folder_id
        )

        # Assert
        assert result.status == "subscribed"
        mock_user_feed_repo.create_user_feed.assert_called_once_with(
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=folder_id,
        )

    @pytest.mark.asyncio
    async def test_subscribe_to_existing_feed_with_invalid_folder(
        self, db_session
    ):
        """Should subscribe at root when folder_id is invalid."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        folder_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=[],
        )
        new_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=None,
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = None
        mock_user_feed_repo.create_user_feed.return_value = new_subscription
        mock_folder_repo = AsyncMock()
        mock_folder_repo.find_by_id.return_value = None
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=folder_id
        )

        # Assert
        assert result.status == "subscribed"
        assert "Folder not found" in result.message
        # Should have called create_user_feed with folder_id=None
        mock_user_feed_repo.create_user_feed.assert_called_once()
        call_kwargs = mock_user_feed_repo.create_user_feed.call_args.kwargs
        assert call_kwargs["folder_id"] is None

    @pytest.mark.asyncio
    async def test_subscribe_to_existing_feed_value_error(self, db_session):
        """Should return 'failed' with actual error message on ValueError."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=[],
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = None
        mock_user_feed_repo.create_user_feed.side_effect = ValueError(
            "Feed limit reached"
        )
        mock_folder_repo = AsyncMock()
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "failed"
        assert result.message == "Feed limit reached"

    @pytest.mark.asyncio
    async def test_subscribe_to_existing_feed_unexpected_error(
        self, db_session
    ):
        """Should return 'failed' with error message on unexpected exception."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=[],
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = None
        mock_user_feed_repo.create_user_feed.side_effect = RuntimeError(
            "Database error"
        )
        mock_folder_repo = AsyncMock()
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "failed"
        assert result.message == "Database error"


class TestDiscoverFeedsNewFeed:
    """Test discover_feeds when feed doesn't exist globally (worker job)."""

    @pytest.mark.asyncio
    async def test_new_feed_with_publisher(self, db_session):
        """Should queue worker job and return 'pending' status."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        user_id = uuid4()
        folder_id = uuid4()
        url = "https://example.com/feed.xml"
        job_id = uuid4()

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = None
        mock_user_feed_repo = AsyncMock()
        mock_folder_repo = AsyncMock()
        mock_folder_repo.find_by_id.return_value = MagicMock(id=folder_id)
        mock_publisher = AsyncMock()
        mock_publisher.publish_create_and_subscribe_with_job.return_value = {
            "job_id": str(job_id),
            "message_id": "msg-123",
        }

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=folder_id
        )

        # Assert
        assert result.status == "pending"
        assert result.message == "Adding feed..."
        mock_publisher.publish_create_and_subscribe_with_job.assert_called_once_with(
            url=url, user_id=user_id, folder_id=folder_id
        )

    @pytest.mark.asyncio
    async def test_new_feed_with_invalid_folder(self, db_session):
        """Should queue worker job with folder_id=None when folder is invalid."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        user_id = uuid4()
        folder_id = uuid4()
        url = "https://example.com/feed.xml"

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = None
        mock_user_feed_repo = AsyncMock()
        mock_folder_repo = AsyncMock()
        mock_folder_repo.find_by_id.return_value = None
        mock_publisher = AsyncMock()
        mock_publisher.publish_create_and_subscribe_with_job.return_value = {
            "job_id": str(uuid4()),
            "message_id": "msg-123",
        }

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=folder_id
        )

        # Assert
        assert result.status == "pending"
        # Should have called with folder_id=None
        mock_publisher.publish_create_and_subscribe_with_job.assert_called_once()
        call_kwargs = mock_publisher.publish_create_and_subscribe_with_job.call_args.kwargs
        assert call_kwargs["folder_id"] is None

    @pytest.mark.asyncio
    async def test_new_feed_without_publisher(self, db_session):
        """Should return 'failed' when DiscoveryPublisher is not configured."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        user_id = uuid4()
        url = "https://example.com/feed.xml"

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = None
        mock_user_feed_repo = AsyncMock()
        mock_folder_repo = AsyncMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=None,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "failed"
        assert result.message == "Service unavailable"

    @pytest.mark.asyncio
    async def test_new_feed_publisher_value_error(self, db_session):
        """Should return 'failed' when publisher raises ValueError."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        user_id = uuid4()
        url = "https://example.com/feed.xml"

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = None
        mock_user_feed_repo = AsyncMock()
        mock_folder_repo = AsyncMock()
        mock_publisher = AsyncMock()
        mock_publisher.publish_create_and_subscribe_with_job.side_effect = (
            ValueError("Invalid URL format")
        )

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "failed"
        assert result.message == "Invalid URL format"

    @pytest.mark.asyncio
    async def test_new_feed_publisher_unexpected_error(self, db_session):
        """Should return 'failed' when publisher raises unexpected exception."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        user_id = uuid4()
        url = "https://example.com/feed.xml"

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = None
        mock_user_feed_repo = AsyncMock()
        mock_folder_repo = AsyncMock()
        mock_publisher = AsyncMock()
        mock_publisher.publish_create_and_subscribe_with_job.side_effect = (
            RuntimeError("Redis connection failed")
        )

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "failed"
        assert result.message == "Redis connection failed"


class TestDiscoverFeedsEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.asyncio
    async def test_subscribe_with_no_latest_articles(self, db_session):
        """Should handle feed with no latest_articles gracefully."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=None,
        )
        new_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=None,
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = None
        mock_user_feed_repo.create_user_feed.return_value = new_subscription
        mock_folder_repo = AsyncMock()
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "subscribed"
        # Should not call bulk_upsert when latest_articles is None/empty
        mock_user_feed_repo.bulk_upsert_user_article_states.assert_not_called()

    @pytest.mark.asyncio
    async def test_subscribe_with_empty_latest_articles(self, db_session):
        """Should handle feed with empty latest_articles list."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=[],
        )
        new_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=None,
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = None
        mock_user_feed_repo.create_user_feed.return_value = new_subscription
        mock_folder_repo = AsyncMock()
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=None
        )

        # Assert
        assert result.status == "subscribed"
        # Should not call bulk_upsert when latest_articles is empty
        mock_user_feed_repo.bulk_upsert_user_article_states.assert_not_called()

    @pytest.mark.asyncio
    async def test_move_to_same_folder_no_op(self, db_session):
        """Should not update when moving to same folder."""
        # Arrange
        mock_db = AsyncMock(spec="AsyncSession")
        feed_id = uuid4()
        user_id = uuid4()
        folder_id = uuid4()
        url = "https://example.com/feed.xml"
        existing_feed = MagicMock(
            id=feed_id,
            title="Example Feed",
            latest_articles=None,
        )
        existing_subscription = UserFeed(
            id=uuid4(),
            user_id=user_id,
            feed_id=feed_id,
            title="Example Feed",
            folder_id=folder_id,
        )

        mock_feed_repo = AsyncMock()
        mock_feed_repo.get_feed_by_url.return_value = existing_feed
        mock_user_feed_repo = AsyncMock()
        mock_user_feed_repo.get_user_subscription.return_value = (
            existing_subscription
        )
        mock_folder_repo = AsyncMock()
        mock_publisher = MagicMock()

        discovery_app = DiscoveryApplication(
            db=mock_db,
            discovery_publisher=mock_publisher,
            feed_application=None,
        )
        discovery_app.feed_repository = mock_feed_repo
        discovery_app.user_feed_repository = mock_user_feed_repo
        discovery_app.folder_repository = mock_folder_repo

        # Act
        result = await discovery_app.discover_feeds(
            url, user_id, folder_id=folder_id
        )

        # Assert
        assert result.status == "existing"
        # folder_id matches, should not update
        mock_user_feed_repo.update_user_feed.assert_not_called()

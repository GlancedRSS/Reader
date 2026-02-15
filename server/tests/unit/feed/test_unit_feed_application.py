"""Unit tests for FeedApplication."""

from uuid import uuid4

import pytest

from backend.application.feed import FeedApplication
from backend.core.exceptions import NotFoundError, ValidationError
from backend.schemas.domain import UserFeedUpdateRequest


class TestFeedApplicationGetList:
    """Test feed list retrieval operations."""

    async def test_get_user_feeds_paginated_empty(self, db_session):
        """Should return empty list when user has no feeds."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser1",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = FeedApplication(db_session)
        result = await app.get_user_feeds_paginated(user.id)

        assert result.data == []
        assert result.pagination.total == 0

    async def test_get_user_feeds_paginated_with_feeds(self, db_session):
        """Should return paginated user feeds."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            UserFeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser2",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)
        user_feed_repo = UserFeedRepository(db_session)

        # Create 3 feeds
        for i in range(3):
            feed = await feed_repo.create_feed(
                url=f"https://example{i}{uuid4()}.com/feed.xml",
                title=f"Feed {i}",
                description="Test",
                feed_type="rss",
                language="en",
                website=f"https://example{i}.com",
                has_articles=False,
            )
            await user_feed_repo.create_user_feed(
                user_id=user.id,
                feed_id=feed.id,
                title=f"My Feed {i}",
                folder_id=None,
            )

        app = FeedApplication(db_session)
        result = await app.get_user_feeds_paginated(user.id, limit=10, offset=0)

        assert len(result.data) == 3
        assert result.pagination.total == 3


class TestFeedApplicationGetById:
    """Test feed detail retrieval operations."""

    async def test_get_user_feed_by_id_success(self, db_session):
        """Should return feed details."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
            UserFeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser3",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        folder_repo = FolderRepository(db_session)
        folder = await folder_repo.create_folder(
            user_id=user.id,
            name="Tech",
            parent_id=None,
        )

        feed_repo = FeedRepository(db_session)
        feed = await feed_repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test Description",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        user_feed_repo = UserFeedRepository(db_session)
        user_feed = await user_feed_repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=folder.id,
        )

        app = FeedApplication(db_session)
        result = await app.get_user_feed_by_id(user_feed.id, user.id)

        assert result.title == "My Feed"
        assert result.description == "Test Description"
        assert result.folder_id == folder.id

    async def test_get_user_feed_by_id_not_found(self, db_session):
        """Should raise NotFoundError when feed doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser4",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = FeedApplication(db_session)

        with pytest.raises(NotFoundError, match="Feed not found"):
            await app.get_user_feed_by_id(uuid4(), user.id)


class TestFeedApplicationUpdate:
    """Test feed update operations."""

    async def test_update_user_feed_title(self, db_session):
        """Should update feed title."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            UserFeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser5",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)
        feed = await feed_repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        user_feed_repo = UserFeedRepository(db_session)
        user_feed = await user_feed_repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="Old Title",
            folder_id=None,
        )

        app = FeedApplication(db_session)
        update_request = UserFeedUpdateRequest(title="New Title")
        result = await app.update_user_feed(
            user_feed.id, update_request, user.id
        )

        assert result.message == "User feed updated successfully"

    async def test_update_user_feed_toggle_pinned(self, db_session):
        """Should toggle feed pinned status."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            UserFeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser6",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)
        feed = await feed_repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        user_feed_repo = UserFeedRepository(db_session)
        user_feed = await user_feed_repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=None,
        )

        app = FeedApplication(db_session)
        update_request = UserFeedUpdateRequest(is_pinned=True)
        await app.update_user_feed(user_feed.id, update_request, user.id)

        # Verify change
        await db_session.refresh(user_feed)
        assert user_feed.is_pinned is True

    async def test_update_user_feed_with_valid_folder(self, db_session):
        """Should update feed folder."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
            UserFeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser7",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        folder_repo = FolderRepository(db_session)
        folder = await folder_repo.create_folder(
            user_id=user.id,
            name="Tech",
            parent_id=None,
        )

        feed_repo = FeedRepository(db_session)
        feed = await feed_repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        user_feed_repo = UserFeedRepository(db_session)
        user_feed = await user_feed_repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=None,
        )

        app = FeedApplication(db_session)
        update_request = UserFeedUpdateRequest(folder_id=folder.id)
        result = await app.update_user_feed(
            user_feed.id, update_request, user.id
        )

        assert result.message == "User feed updated successfully"

        # Verify change
        await db_session.refresh(user_feed)
        assert user_feed.folder_id == folder.id

    async def test_update_user_feed_with_invalid_folder_raises(
        self, db_session
    ):
        """Should raise ValidationError when folder doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            UserFeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser8",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)
        feed = await feed_repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        user_feed_repo = UserFeedRepository(db_session)
        user_feed = await user_feed_repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=None,
        )

        app = FeedApplication(db_session)
        update_request = UserFeedUpdateRequest(folder_id=uuid4())

        with pytest.raises(ValidationError, match="Invalid folder ID"):
            await app.update_user_feed(user_feed.id, update_request, user.id)

    async def test_update_user_feed_not_found_raises(self, db_session):
        """Should raise NotFoundError when feed doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser9",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = FeedApplication(db_session)
        update_request = UserFeedUpdateRequest(title="New Title")

        with pytest.raises(NotFoundError, match="Feed not found"):
            await app.update_user_feed(uuid4(), update_request, user.id)


class TestFeedApplicationUnsubscribe:
    """Test feed unsubscribe operations."""

    async def test_unsubscribe_from_feed_success(self, db_session):
        """Should unsubscribe from feed successfully."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            UserFeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser10",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)
        feed = await feed_repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        user_feed_repo = UserFeedRepository(db_session)
        user_feed = await user_feed_repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="To Unsubscribe",
            folder_id=None,
        )

        app = FeedApplication(db_session)
        result = await app.unsubscribe_from_feed(user_feed.id, user.id)

        assert result.message == "Successfully unsubscribed"

        # Verify deletion
        found = await user_feed_repo.get_user_feed_by_id(user_feed.id)
        assert found is None

    async def test_unsubscribe_from_feed_not_found_raises(self, db_session):
        """Should raise NotFoundError when feed doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser11",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = FeedApplication(db_session)

        with pytest.raises(NotFoundError, match="Feed not found"):
            await app.unsubscribe_from_feed(uuid4(), user.id)


class TestFeedApplicationBackfillTags:
    """Test tag backfill operations."""

    async def test_backfill_tags_for_articles_empty_list(self, db_session):
        """Should return 0 when article_ids is empty."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="feedappuser12",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = FeedApplication(db_session)
        result = await app._backfill_tags_for_articles(user.id, [])

        assert result == 0

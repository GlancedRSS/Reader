"""Unit tests for FeedRepository."""

from datetime import UTC, datetime
from uuid import uuid4

from backend.infrastructure.repositories.feed import FeedRepository


class TestFeedRepositoryCreate:
    """Test feed creation operations."""

    async def test_create_feed_with_minimal_fields(self, db_session):
        """Should create a feed with minimal required fields."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser1",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FeedRepository(db_session)
        feed = await repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test Description",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        assert feed.id is not None
        assert feed.title == "Test Feed"
        assert feed.feed_type == "rss"
        assert feed.is_active is True
        assert feed.error_count == 0

    async def test_create_feed_with_articles(self, db_session):
        """Should create a feed with latest articles."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser2",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        article_ids = [uuid4(), uuid4(), uuid4()]

        repo = FeedRepository(db_session)
        feed = await repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test Description",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=True,
        )

        # Update with latest articles
        updated = await repo.update_feed(
            feed.id, {"latest_articles": article_ids}
        )
        assert updated.latest_articles == article_ids


class TestFeedRepositoryFind:
    """Test feed retrieval operations."""

    async def test_get_feed_by_id_when_exists(self, db_session):
        """Should return feed when it exists."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser3",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FeedRepository(db_session)
        created = await repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test Description",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        found = await repo.get_feed_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.title == "Test Feed"

    async def test_get_feed_by_id_returns_none_when_not_exists(
        self, db_session
    ):
        """Should return None when feed doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser4",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FeedRepository(db_session)
        found = await repo.get_feed_by_id(uuid4())

        assert found is None

    async def test_get_feed_by_url_when_exists(self, db_session):
        """Should return feed when URL exists."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser5",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        unique_url = f"https://example{uuid4()}.com/feed.xml"
        repo = FeedRepository(db_session)
        created = await repo.create_feed(
            url=unique_url,
            title="Test Feed",
            description="Test Description",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        found = await repo.get_feed_by_url(unique_url)

        assert found is not None
        assert found.id == created.id

    async def test_get_feed_by_url_returns_none_when_not_exists(
        self, db_session
    ):
        """Should return None when URL doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser6",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FeedRepository(db_session)
        found = await repo.get_feed_by_url("https://nonexistent.com/feed.xml")

        assert found is None


class TestFeedRepositoryUpdate:
    """Test feed update operations."""

    async def test_update_feed_modifies_fields(self, db_session):
        """Should update specified feed fields."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser7",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FeedRepository(db_session)
        feed = await repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Old Title",
            description="Old Description",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        updated = await repo.update_feed(
            feed.id,
            {
                "title": "New Title",
                "description": "New Description",
                "last_update": datetime.now(UTC),
            },
        )

        assert updated.title == "New Title"
        assert updated.description == "New Description"

    async def test_update_feed_non_existent_raises(self, db_session):
        """Should return None when feed doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser8",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FeedRepository(db_session)

        result = await repo.update_feed(
            uuid4(),
            {"title": "New Title"},
        )

        assert result is None


class TestFeedRepositoryDelete:
    """Test feed delete operations."""

    async def test_delete_feed_removes_feed(self, db_session):
        """Should delete the feed."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser9",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = FeedRepository(db_session)
        feed = await repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="To Delete",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=False,
        )

        await repo.delete_feed(feed)
        await db_session.flush()

        # Verify feed is deleted
        found = await repo.get_feed_by_id(feed.id)
        assert found is None


class TestFeedRepositoryGetArticleIds:
    """Test article ID retrieval operations."""

    async def test_get_article_ids_for_feed(self, db_session):
        """Should get article IDs for a feed."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="feeduser10",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        article_ids = [uuid4(), uuid4(), uuid4()]

        repo = FeedRepository(db_session)
        feed = await repo.create_feed(
            url=f"https://example{uuid4()}.com/feed.xml",
            title="Test Feed",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example.com",
            has_articles=True,
        )

        await repo.update_feed(feed.id, {"latest_articles": article_ids})

        # Get article IDs via query
        from sqlalchemy import select

        from backend.models import Feed

        result = await db_session.execute(
            select(Feed).where(Feed.id == feed.id)
        )
        fetched_feed = result.scalar_one_or_none()

        assert fetched_feed is not None
        assert fetched_feed.latest_articles == article_ids

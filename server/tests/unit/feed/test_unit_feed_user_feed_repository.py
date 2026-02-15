"""Unit tests for UserFeedRepository."""

from uuid import uuid4

from backend.infrastructure.repositories.user_feed import UserFeedRepository
from backend.models import Article, ArticleSource


class TestUserFeedRepositoryCreate:
    """Test user feed creation operations."""

    async def test_create_user_feed_at_root(self, db_session):
        """Should create a user feed without folder (root level)."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser1",
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

        repo = UserFeedRepository(db_session)
        user_feed = await repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=None,
        )

        assert user_feed.id is not None
        assert user_feed.user_id == user.id
        assert user_feed.feed_id == feed.id
        assert user_feed.title == "My Feed"
        assert user_feed.folder_id is None
        assert user_feed.is_pinned is False
        assert user_feed.is_active is True

    async def test_create_user_feed_with_folder(self, db_session):
        """Should create a user feed with a folder."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser2",
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

        repo = UserFeedRepository(db_session)
        user_feed = await repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=folder.id,
        )

        assert user_feed.folder_id == folder.id


class TestUserFeedRepositoryFind:
    """Test user feed retrieval operations."""

    async def test_get_user_feed_by_id_when_exists(self, db_session):
        """Should return user feed when it exists."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser3",
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

        repo = UserFeedRepository(db_session)
        created = await repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=folder.id,
        )

        found = await repo.get_user_feed_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.title == "My Feed"

    async def test_get_user_feed_by_id_returns_none_when_not_exists(
        self, db_session
    ):
        """Should return None when user feed doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="userfeeduser4",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserFeedRepository(db_session)
        found = await repo.get_user_feed_by_id(uuid4())

        assert found is None

    async def test_get_user_subscription_when_exists(self, db_session):
        """Should return user subscription when it exists."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser5",
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

        repo = UserFeedRepository(db_session)
        await repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="My Feed",
            folder_id=folder.id,
        )

        subscription = await repo.get_user_subscription(user.id, feed.id)

        assert subscription is not None
        assert subscription.feed_id == feed.id

    async def test_get_user_subscription_returns_none_when_not_exists(
        self, db_session
    ):
        """Should return None when subscription doesn't exist."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser6",
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

        repo = UserFeedRepository(db_session)
        subscription = await repo.get_user_subscription(user.id, feed.id)

        assert subscription is None


class TestUserFeedRepositoryUpdate:
    """Test user feed update operations."""

    async def test_update_user_feed_modifies_fields(self, db_session):
        """Should update specified user feed fields."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser7",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        folder_repo = FolderRepository(db_session)
        await folder_repo.create_folder(
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

        repo = UserFeedRepository(db_session)
        user_feed = await repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="Old Title",
            folder_id=None,
        )

        await repo.update_user_feed(
            user_feed, {"title": "New Title", "is_pinned": True}
        )

        # Refresh to get updated values
        await db_session.refresh(user_feed)

        assert user_feed.title == "New Title"
        assert user_feed.is_pinned is True


class TestUserFeedRepositoryDelete:
    """Test user feed delete operations."""

    async def test_delete_user_feed_removes_feed(self, db_session):
        """Should delete the user feed."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser8",
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

        repo = UserFeedRepository(db_session)
        user_feed = await repo.create_user_feed(
            user_id=user.id,
            feed_id=feed.id,
            title="To Delete",
            folder_id=folder.id,
        )

        await repo.delete_user_feed(user_feed)

        # Verify user feed is deleted
        found = await repo.get_user_feed_by_id(user_feed.id)
        assert found is None


class TestUserFeedRepositoryValidation:
    """Test validation operations."""

    async def test_validate_folder_for_user_when_valid(self, db_session):
        """Should return folder when it belongs to user."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import FolderRepository
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser9",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        folder_repo = FolderRepository(db_session)
        folder = await folder_repo.create_folder(
            user_id=user.id,
            name="Tech",
            parent_id=None,
        )

        repo = UserFeedRepository(db_session)
        result = await repo.validate_folder_for_user(user.id, folder.id)

        assert result is not None
        assert result.id == folder.id

    async def test_validate_folder_for_user_returns_none_when_invalid(
        self, db_session
    ):
        """Should return None when folder doesn't exist or belongs to different user."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser10",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserFeedRepository(db_session)
        result = await repo.validate_folder_for_user(user.id, uuid4())

        assert result is None


class TestUserFeedRepositoryPagination:
    """Test paginated queries."""

    async def test_get_user_feeds_count(self, db_session):
        """Should return count of user feeds."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
            FolderRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser11",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        folder_repo = FolderRepository(db_session)
        folder = await folder_repo.create_folder(
            user_id=user.id,
            name="Tech",
            parent_id=None,
        )

        feed_repo = FeedRepository(db_session)

        repo = UserFeedRepository(db_session)

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
            await repo.create_user_feed(
                user_id=user.id,
                feed_id=feed.id,
                title=f"My Feed {i}",
                folder_id=folder.id,
            )

        count = await repo.get_user_feeds_count(user.id, folder.id, all=False)

        assert count == 3

    async def test_get_user_feeds_paginated(self, db_session):
        """Should return paginated user feeds."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import (
            FeedRepository,
        )
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="userfeeduser12",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)

        repo = UserFeedRepository(db_session)

        # Create 5 feeds
        for i in range(5):
            feed = await feed_repo.create_feed(
                url=f"https://example{i}{uuid4()}.com/feed.xml",
                title=f"Feed {i}",
                description="Test",
                feed_type="rss",
                language="en",
                website=f"https://example{i}.com",
                has_articles=False,
            )
            await repo.create_user_feed(
                user_id=user.id,
                feed_id=feed.id,
                title=f"Feed {i}",
                folder_id=None,
            )

        # Get first page
        result = await repo.get_user_feeds_paginated(
            user_id=user.id,
            limit=3,
            offset=0,
            order_by="name_asc",
            folder_id=None,
            all=False,
        )

        assert len(result) == 3


class TestUserFeedRepositoryUnsubscribeHelpers:
    """Test unsubscribe helper methods."""

    async def test_get_article_ids_for_feeds_returns_unique_ids(
        self, db_session
    ):
        """Should return unique article IDs for multiple feeds."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import FeedRepository
        from backend.infrastructure.repositories.user import UserRepository

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="helperuser1",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)

        # Create 2 feeds
        feed1 = await feed_repo.create_feed(
            url=f"https://example1{uuid4()}.com/feed.xml",
            title="Feed 1",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example1.com",
            has_articles=False,
        )

        feed2 = await feed_repo.create_feed(
            url=f"https://example2{uuid4()}.com/feed.xml",
            title="Feed 2",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://example2.com",
            has_articles=False,
        )

        # Create articles first (required for foreign key constraint)
        article1 = Article(
            title="Article 1",
            canonical_url="https://example.com/1",
        )
        article2 = Article(
            title="Article 2",
            canonical_url="https://example.com/2",
        )
        article3 = Article(
            title="Article 3",
            canonical_url="https://example.com/3",
        )
        shared_article = Article(
            title="Shared Article",
            canonical_url="https://example.com/shared",
        )
        db_session.add(article1)
        db_session.add(article2)
        db_session.add(article3)
        db_session.add(shared_article)
        await db_session.flush()

        # Create ArticleSource entries
        db_session.add(ArticleSource(article_id=article1.id, feed_id=feed1.id))
        db_session.add(ArticleSource(article_id=article2.id, feed_id=feed1.id))
        db_session.add(
            ArticleSource(article_id=shared_article.id, feed_id=feed1.id)
        )
        db_session.add(ArticleSource(article_id=article3.id, feed_id=feed2.id))
        db_session.add(
            ArticleSource(article_id=shared_article.id, feed_id=feed2.id)
        )
        await db_session.flush()

        repo = UserFeedRepository(db_session)
        result = await repo.get_article_ids_for_feeds([feed1.id, feed2.id])

        # Should return 4 unique articles (shared_article appears twice in db)
        assert len(result) == 4
        assert article1.id in result
        assert article2.id in result
        assert article3.id in result
        assert shared_article.id in result

    async def test_get_article_ids_for_feeds_empty_list(self, db_session):
        """Should return empty list when feed_ids is empty."""
        from backend.infrastructure.repositories.user_feed import (
            UserFeedRepository,
        )

        repo = UserFeedRepository(db_session)
        result = await repo.get_article_ids_for_feeds([])

        assert result == []

    async def test_get_article_ids_accessible_via_other_feeds_single_exclude(
        self, db_session
    ):
        """Should find articles accessible via other feeds when excluding one."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import FeedRepository
        from backend.infrastructure.repositories.user import UserRepository
        from backend.models import UserFeed

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="helperuser2",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)

        # Create 3 feeds
        feed1 = await feed_repo.create_feed(
            url=f"https://ex1{uuid4()}.com/feed.xml",
            title="Feed 1",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://ex1.com",
            has_articles=False,
        )

        feed2 = await feed_repo.create_feed(
            url=f"https://ex2{uuid4()}.com/feed.xml",
            title="Feed 2",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://ex2.com",
            has_articles=False,
        )

        feed3 = await feed_repo.create_feed(
            url=f"https://ex3{uuid4()}.com/feed.xml",
            title="Feed 3",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://ex3.com",
            has_articles=False,
        )

        # User is subscribed to feed1 and feed2 (not feed3)
        db_session.add(
            UserFeed(user_id=user.id, feed_id=feed1.id, title="Feed 1")
        )
        db_session.add(
            UserFeed(user_id=user.id, feed_id=feed2.id, title="Feed 2")
        )
        await db_session.flush()

        # Create articles first (required for foreign key constraint)
        article_only_in_feed1 = Article(
            title="Article 1",
            canonical_url="https://example.com/ex1",
        )
        article_in_feed1_and_feed3 = Article(
            title="Article 2",
            canonical_url="https://example.com/ex2",
        )
        article_in_all_feeds = Article(
            title="Article 3",
            canonical_url="https://example.com/ex3",
        )
        db_session.add(article_only_in_feed1)
        db_session.add(article_in_feed1_and_feed3)
        db_session.add(article_in_all_feeds)
        await db_session.flush()

        # ArticleSource entries
        db_session.add(
            ArticleSource(article_id=article_only_in_feed1.id, feed_id=feed1.id)
        )
        db_session.add(
            ArticleSource(
                article_id=article_in_feed1_and_feed3.id, feed_id=feed1.id
            )
        )
        db_session.add(
            ArticleSource(
                article_id=article_in_feed1_and_feed3.id, feed_id=feed3.id
            )
        )
        db_session.add(
            ArticleSource(article_id=article_in_all_feeds.id, feed_id=feed1.id)
        )
        db_session.add(
            ArticleSource(article_id=article_in_all_feeds.id, feed_id=feed2.id)
        )
        db_session.add(
            ArticleSource(article_id=article_in_all_feeds.id, feed_id=feed3.id)
        )
        await db_session.flush()

        repo = UserFeedRepository(db_session)
        article_ids = [
            article_only_in_feed1.id,
            article_in_feed1_and_feed3.id,
            article_in_all_feeds.id,
        ]

        # Exclude feed1 - should find articles accessible via feed2
        result = await repo.get_article_ids_accessible_via_other_feeds(
            user.id, article_ids, [feed1.id]
        )

        # article_in_all_feeds is accessible via feed2
        # article_in_feed1_and_feed3 is NOT accessible (feed3 not subscribed)
        # article_only_in_feed1 is NOT accessible (only in feed1 which is excluded)
        assert article_in_all_feeds.id in result
        assert article_in_feed1_and_feed3.id not in result
        assert article_only_in_feed1.id not in result

    async def test_get_article_ids_accessible_via_other_feeds_multiple_excludes(
        self, db_session
    ):
        """Should find articles accessible via other feeds when excluding multiple."""
        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories import FeedRepository
        from backend.infrastructure.repositories.user import UserRepository
        from backend.models import UserFeed

        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="helperuser3",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        feed_repo = FeedRepository(db_session)

        # Create 3 feeds
        feed1 = await feed_repo.create_feed(
            url=f"https://multi1{uuid4()}.com/feed.xml",
            title="Feed 1",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://multi1.com",
            has_articles=False,
        )

        feed2 = await feed_repo.create_feed(
            url=f"https://multi2{uuid4()}.com/feed.xml",
            title="Feed 2",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://multi2.com",
            has_articles=False,
        )

        feed3 = await feed_repo.create_feed(
            url=f"https://multi3{uuid4()}.com/feed.xml",
            title="Feed 3",
            description="Test",
            feed_type="rss",
            language="en",
            website="https://multi3.com",
            has_articles=False,
        )

        # User is subscribed to all 3 feeds
        db_session.add(
            UserFeed(user_id=user.id, feed_id=feed1.id, title="Feed 1")
        )
        db_session.add(
            UserFeed(user_id=user.id, feed_id=feed2.id, title="Feed 2")
        )
        db_session.add(
            UserFeed(user_id=user.id, feed_id=feed3.id, title="Feed 3")
        )
        await db_session.flush()

        # Create articles first (required for foreign key constraint)
        article_in_feed1_only = Article(
            title="Article 1",
            canonical_url="https://example.com/multi1",
        )
        article_in_feed1_and_feed2 = Article(
            title="Article 2",
            canonical_url="https://example.com/multi2",
        )
        article_in_all_feeds = Article(
            title="Article 3",
            canonical_url="https://example.com/multi3",
        )
        db_session.add(article_in_feed1_only)
        db_session.add(article_in_feed1_and_feed2)
        db_session.add(article_in_all_feeds)
        await db_session.flush()

        # ArticleSource entries
        db_session.add(
            ArticleSource(article_id=article_in_feed1_only.id, feed_id=feed1.id)
        )
        db_session.add(
            ArticleSource(
                article_id=article_in_feed1_and_feed2.id, feed_id=feed1.id
            )
        )
        db_session.add(
            ArticleSource(
                article_id=article_in_feed1_and_feed2.id, feed_id=feed2.id
            )
        )
        db_session.add(
            ArticleSource(article_id=article_in_all_feeds.id, feed_id=feed1.id)
        )
        db_session.add(
            ArticleSource(article_id=article_in_all_feeds.id, feed_id=feed2.id)
        )
        db_session.add(
            ArticleSource(article_id=article_in_all_feeds.id, feed_id=feed3.id)
        )
        await db_session.flush()

        repo = UserFeedRepository(db_session)
        article_ids = [
            article_in_feed1_only.id,
            article_in_feed1_and_feed2.id,
            article_in_all_feeds.id,
        ]

        # Exclude feed1 and feed2 - should find articles accessible via feed3 only
        result = await repo.get_article_ids_accessible_via_other_feeds(
            user.id, article_ids, [feed1.id, feed2.id]
        )

        # article_in_all_feeds is accessible via feed3
        # article_in_feed1_and_feed2 is NOT accessible (both feeds excluded)
        # article_in_feed1_only is NOT accessible (only in feed1 which is excluded)
        assert article_in_all_feeds.id in result
        assert article_in_feed1_and_feed2.id not in result
        assert article_in_feed1_only.id not in result

    async def test_get_article_ids_accessible_via_other_feeds_empty_article_ids(
        self, db_session
    ):
        """Should return empty set when article_ids is empty."""
        from backend.infrastructure.repositories.user_feed import (
            UserFeedRepository,
        )

        repo = UserFeedRepository(db_session)
        result = await repo.get_article_ids_accessible_via_other_feeds(
            uuid4(), [], [uuid4()]
        )

        assert result == set()

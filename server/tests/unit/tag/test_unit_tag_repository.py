"""Unit tests for UserTagRepository."""

from uuid import uuid4

import pytest

from backend.infrastructure.auth.security import PasswordHasher
from backend.infrastructure.repositories.tag import UserTagRepository
from backend.infrastructure.repositories.user import UserRepository


class TestTagRepositoryCreate:
    """Test tag creation operations."""

    async def test_create_tag(self, db_session):
        """Should create a new tag."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser1",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        tag = await repo.create_tag(user_id=user.id, name="Work")

        assert tag.id is not None
        assert tag.name == "Work"
        assert tag.user_id == user.id
        assert tag.article_count == 0

    async def test_create_tag_preserves_name(self, db_session):
        """Should preserve tag name as provided (sanitization happens at application layer)."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser2",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        # Repository doesn't sanitize - it just stores what's given
        tag = await repo.create_tag(user_id=user.id, name="Work")

        assert tag.name == "Work"

    async def test_create_tag_duplicate_raises_integrity_error(
        self, db_session
    ):
        """Should raise IntegrityError for duplicate tag name per user."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser3",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        await repo.create_tag(user_id=user.id, name="Work")

        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await repo.create_tag(user_id=user.id, name="Work")

    async def test_create_tag_same_name_different_users_succeeds(
        self, db_session
    ):
        """Should allow same tag name for different users."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user1 = await user_repo.create_user(
            username="taguser4",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        user2 = await user_repo.create_user(
            username="taguser5",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        tag1 = await repo.create_tag(user_id=user1.id, name="Work")
        tag2 = await repo.create_tag(user_id=user2.id, name="Work")

        assert tag1.name == tag2.name
        assert tag1.user_id != tag2.user_id


class TestTagRepositoryFind:
    """Test tag retrieval operations."""

    async def test_find_by_user_and_name_when_exists(self, db_session):
        """Should return tag when it exists."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser6",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        created = await repo.create_tag(user_id=user.id, name="Work")

        found = await repo.find_by_user_and_name(user.id, "Work")

        assert found is not None
        assert found.id == created.id

    async def test_find_by_user_and_name_returns_none_when_not_exists(
        self, db_session
    ):
        """Should return None when tag doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser7",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        found = await repo.find_by_user_and_name(user.id, "NonExistent")

        assert found is None

    async def test_find_by_id_and_user_when_exists(self, db_session):
        """Should return tag when it exists and belongs to user."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser8",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        created = await repo.create_tag(user_id=user.id, name="Test")

        found = await repo.find_by_id(tag_id=created.id, user_id=user.id)

        assert found is not None
        assert found.id == created.id

    async def test_find_by_id_returns_none_when_not_exists(self, db_session):
        """Should return None when tag doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser9",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        found = await repo.find_by_id(tag_id=uuid4(), user_id=user.id)

        assert found is None

    async def test_find_by_id_returns_none_for_different_user(self, db_session):
        """Should return None when tag exists but belongs to different user."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user1 = await user_repo.create_user(
            username="taguser10",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        user2 = await user_repo.create_user(
            username="taguser11",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        tag = await repo.create_tag(user_id=user1.id, name="Secret")

        found = await repo.find_by_id(tag_id=tag.id, user_id=user2.id)

        assert found is None


class TestTagRepositoryGetAll:
    """Test getting all user tags."""

    async def test_get_user_tags_returns_all_ordered_by_name(self, db_session):
        """Should return all tags ordered alphabetically."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser12",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        await repo.create_tag(user_id=user.id, name="Zebra")
        await repo.create_tag(user_id=user.id, name="Apple")
        await repo.create_tag(user_id=user.id, name="Banana")

        tags = await repo.get_user_tags(user.id)

        assert len(tags) == 3
        assert tags[0].name == "Apple"
        assert tags[1].name == "Banana"
        assert tags[2].name == "Zebra"

    async def test_get_user_tags_filters_by_user(self, db_session):
        """Should only return tags for specified user."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user1 = await user_repo.create_user(
            username="taguser13",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        user2 = await user_repo.create_user(
            username="taguser14",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        await repo.create_tag(user_id=user1.id, name="User1Tag")
        await repo.create_tag(user_id=user2.id, name="User2Tag")

        tags = await repo.get_user_tags(user1.id)

        assert len(tags) == 1
        assert tags[0].name == "User1Tag"

    async def test_get_user_tags_paginated(self, db_session):
        """Should return paginated tags with total count."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser15",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        for i in range(5):
            await repo.create_tag(user_id=user.id, name=f"Tag{i}")

        tags, total = await repo.get_user_tags_paginated(
            user.id, limit=2, offset=0
        )

        assert len(tags) == 2
        assert total == 5

    async def test_get_user_tags_paginated_with_offset(self, db_session):
        """Should skip tags with offset."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser16",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        for i in range(5):
            await repo.create_tag(user_id=user.id, name=f"Tag{i}")

        tags, total = await repo.get_user_tags_paginated(
            user.id, limit=2, offset=2
        )

        assert len(tags) == 2
        assert total == 5


class TestTagRepositoryUpdate:
    """Test tag update operations."""

    async def test_update_tag_modifies_name(self, db_session):
        """Should update tag name."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser17",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        tag = await repo.create_tag(user_id=user.id, name="Old Name")

        await repo.update_tag(tag, {"name": "New Name"})

        await db_session.refresh(tag)
        assert tag.name == "New Name"

    async def test_update_tag_with_duplicate_name_raises_integrity_error(
        self, db_session
    ):
        """Should raise IntegrityError for duplicate name."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser18",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        await repo.create_tag(user_id=user.id, name="Work")
        tag2 = await repo.create_tag(user_id=user.id, name="Personal")

        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await repo.update_tag(tag2, {"name": "Work"})


class TestTagRepositoryDelete:
    """Test tag delete operations."""

    async def test_delete_tag_removes_tag(self, db_session):
        """Should delete the tag."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser19",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        tag = await repo.create_tag(user_id=user.id, name="Delete Me")

        await repo.delete_tag(tag)

        found = await repo.find_by_id(tag.id, user.id)
        assert found is None


class TestTagRepositoryGetOrCreate:
    """Test get-or-create operations."""

    async def test_get_or_create_tag_returns_existing(self, db_session):
        """Should return existing tag."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser21",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        tag1 = await repo.create_tag(user_id=user.id, name="Work")
        tag2 = await repo.get_or_create_tag(user.id, "Work")

        assert tag1.id == tag2.id

    async def test_get_or_create_tag_creates_new(self, db_session):
        """Should create new tag if not exists."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser22",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)
        tag = await repo.get_or_create_tag(user.id, "Work")

        assert tag.id is not None
        assert tag.name == "Work"


class TestTagRepositoryArticleTags:
    """Test article-tag relationship operations."""

    async def test_get_article_tags_no_user_article_returns_empty(
        self, db_session
    ):
        """Should return empty list when UserArticle doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser23",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)

        # Use a random article ID that doesn't exist
        tags = await repo.get_article_tags(uuid4(), user.id)

        assert tags == []

    async def test_add_tags_to_article_no_user_article_raises(self, db_session):
        """Should raise ValueError when UserArticle doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser24",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)

        # Create tag
        tag1 = await repo.create_tag(user_id=user.id, name="Work")

        # Use a random article ID that doesn't exist
        with pytest.raises(ValueError, match="Article not found for user"):
            await repo.add_tags_to_article(uuid4(), [tag1.id], user.id)

    async def test_remove_tags_from_article_no_user_article_returns_empty(
        self, db_session
    ):
        """Should return empty list when UserArticle doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser25",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)

        # Create tag
        tag1 = await repo.create_tag(user_id=user.id, name="Work")

        # Use a random article ID that doesn't exist
        removed = await repo.remove_tags_from_article(
            uuid4(), [tag1.id], user.id
        )

        assert removed == []

    async def test_remove_articles_from_all_tags_empty_list_returns_zero(
        self, db_session
    ):
        """Should return 0 when article_ids list is empty."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="taguser26",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        repo = UserTagRepository(db_session)

        count = await repo.remove_articles_from_all_tags([], user.id)

        assert count == 0

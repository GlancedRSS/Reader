"""Unit tests for TagApplication."""

from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from backend.application.tag import TagApplication
from backend.core.exceptions import (
    ConflictError,
    NotFoundError,
)
from backend.infrastructure.auth.security import PasswordHasher
from backend.infrastructure.repositories.user import UserRepository
from backend.schemas.domain import TagCreateRequest, TagUpdateRequest


class TestTagApplicationCreate:
    """Test tag creation operations."""

    async def test_create_tag(self, db_session):
        """Should create a tag successfully."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser1",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        request = TagCreateRequest(name="Work")

        response = await app.create_user_tag(user.id, request)

        assert response.id is not None
        assert response.name == "Work"
        assert response.article_count == 0

    async def test_create_tag_sanitizes_name(self, db_session):
        """Should sanitize tag name before creating."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser2",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        request = TagCreateRequest(name="  Work  ")

        response = await app.create_user_tag(user.id, request)

        assert response.name == "Work"

    async def test_create_tag_with_duplicate_name_returns_existing(
        self, db_session
    ):
        """Should return existing tag for duplicate name (get-or-create)."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser3",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        request = TagCreateRequest(name="Work")

        response1 = await app.create_user_tag(user.id, request)
        response2 = await app.create_user_tag(user.id, request)

        assert response1.id == response2.id

    async def test_create_tag_with_empty_name_raises(self, db_session):
        """Should raise ValidationError for empty name."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="appuser4",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        TagApplication(db_session)

        # Pydantic validates before application layer
        with pytest.raises(PydanticValidationError):
            TagCreateRequest(name="")

    async def test_create_tag_with_too_long_name_raises(self, db_session):
        """Should raise ValidationError for name exceeding max length."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        await user_repo.create_user(
            username="appuser5",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        TagApplication(db_session)

        # Pydantic validates before application layer
        with pytest.raises(PydanticValidationError):
            TagCreateRequest(name="a" * 65)


class TestTagApplicationUpdate:
    """Test tag update operations."""

    async def test_update_tag_name(self, db_session):
        """Should update tag name."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser6",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        create_request = TagCreateRequest(name="Old Name")
        tag = await app.create_user_tag(user.id, create_request)

        update_request = TagUpdateRequest(name="New Name")
        response = await app.update_user_tag(user.id, tag.id, update_request)

        assert response.message == "Tag updated successfully"

    async def test_update_tag_with_duplicate_name_raises(self, db_session):
        """Should raise ConflictError for duplicate name."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser7",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)

        await app.create_user_tag(user.id, TagCreateRequest(name="Work"))
        tag2 = await app.create_user_tag(
            user.id, TagCreateRequest(name="Personal")
        )

        update_request = TagUpdateRequest(name="Work")

        with pytest.raises(ConflictError, match="already exists"):
            await app.update_user_tag(user.id, tag2.id, update_request)

    async def test_update_tag_non_existent_raises(self, db_session):
        """Should raise NotFoundError when tag doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser8",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        update_request = TagUpdateRequest(name="New Name")

        with pytest.raises(NotFoundError, match="Tag not found"):
            await app.update_user_tag(user.id, uuid4(), update_request)

    async def test_update_tag_with_invalid_name_raises(self, db_session):
        """Should raise ValidationError for invalid name."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser9",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        await app.create_user_tag(user.id, TagCreateRequest(name="Work"))

        # Pydantic validates before application layer
        with pytest.raises(PydanticValidationError):
            TagUpdateRequest(name="")


class TestTagApplicationDelete:
    """Test tag delete operations."""

    async def test_delete_tag(self, db_session):
        """Should delete tag successfully."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser10",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        tag = await app.create_user_tag(
            user.id, TagCreateRequest(name="Delete Me")
        )

        response = await app.delete_user_tag(user.id, tag.id)

        assert response.message == "Tag deleted successfully"

    async def test_delete_tag_non_existent_raises(self, db_session):
        """Should raise NotFoundError when tag doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser11",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)

        with pytest.raises(NotFoundError, match="Tag not found"):
            await app.delete_user_tag(user.id, uuid4())


class TestTagApplicationGetDetails:
    """Test tag retrieval operations."""

    async def test_get_user_tag(self, db_session):
        """Should return tag details."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser12",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)
        created = await app.create_user_tag(
            user.id, TagCreateRequest(name="Work")
        )

        tag = await app.get_user_tag(user.id, created.id)

        assert tag.id == created.id
        assert tag.name == "Work"

    async def test_get_user_tag_non_existent_raises(self, db_session):
        """Should raise NotFoundError when tag doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser13",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)

        with pytest.raises(NotFoundError, match="Tag not found"):
            await app.get_user_tag(user.id, uuid4())

    async def test_get_user_tags(self, db_session):
        """Should return all user tags with pagination."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser14",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)

        await app.create_user_tag(user.id, TagCreateRequest(name="Zebra"))
        await app.create_user_tag(user.id, TagCreateRequest(name="Apple"))
        await app.create_user_tag(user.id, TagCreateRequest(name="Banana"))

        response = await app.get_user_tags(user.id, limit=10, offset=0)

        assert len(response.data) == 3
        assert response.pagination.total == 3
        # Should be alphabetically ordered
        assert response.data[0].name == "Apple"
        assert response.data[1].name == "Banana"
        assert response.data[2].name == "Zebra"

    async def test_get_user_tags_paginated(self, db_session):
        """Should respect pagination parameters."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser15",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)

        for i in range(5):
            await app.create_user_tag(user.id, TagCreateRequest(name=f"Tag{i}"))

        page1 = await app.get_user_tags(user.id, limit=2, offset=0)

        assert len(page1.data) == 2
        assert page1.pagination.total == 5
        assert page1.pagination.has_more is True

        page2 = await app.get_user_tags(user.id, limit=2, offset=2)

        assert len(page2.data) == 2
        assert page2.pagination.has_more is True

        page3 = await app.get_user_tags(user.id, limit=2, offset=4)

        assert len(page3.data) == 1
        assert page3.pagination.has_more is False


class TestTagApplicationSync:
    """Test article tag sync operations."""

    async def test_sync_article_tags_no_user_article_raises_value_error(
        self, db_session
    ):
        """Should raise ValueError when UserArticle doesn't exist."""
        user_repo = UserRepository(db_session)
        password_hasher = PasswordHasher()
        user = await user_repo.create_user(
            username="appuser16",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = TagApplication(db_session)

        # Create tag
        tag1 = await app.create_user_tag(user.id, TagCreateRequest(name="Work"))

        # Use a random article ID that doesn't exist
        # Sync should raise ValueError when UserArticle doesn't exist
        with pytest.raises(ValueError, match=r"Article not found for user"):
            await app.sync_article_tags(user.id, uuid4(), [tag1.id])

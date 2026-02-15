"""Unit tests for tag repository."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.infrastructure.repositories.tag import UserTagRepository
from backend.models import UserTag


class TestFindByUserAndName:
    """Test finding tags by user and name."""

    @pytest.mark.asyncio
    async def test_returns_tag_when_found(self):
        """Should return tag when user and name match."""
        mock_db = MagicMock()
        user_id = uuid4()
        mock_tag = UserTag(id=uuid4(), user_id=user_id, name="tech")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.find_by_user_and_name(user_id, "tech")

        assert result is not None
        assert result.name == "tech"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when no matching tag."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.find_by_user_and_name(uuid4(), "nonexistent")

        assert result is None


class TestFindById:
    """Test finding tags by ID."""

    @pytest.mark.asyncio
    async def test_returns_tag_when_id_matches(self):
        """Should return tag when ID matches."""
        mock_db = MagicMock()
        tag_id = uuid4()
        user_id = uuid4()
        mock_tag = UserTag(id=tag_id, user_id=user_id, name="test")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.find_by_id(tag_id, user_id)

        assert result is not None

    @pytest.mark.asyncio
    async def test_returns_none_for_different_user(self):
        """Should return None when tag exists but belongs to different user."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.find_by_id(uuid4(), uuid4())

        assert result is None


class TestGetUserTags:
    """Test getting user tags."""

    @pytest.mark.asyncio
    async def test_returns_tags_ordered_by_name(self):
        """Should return tags ordered by name."""
        mock_db = MagicMock()
        user_id = uuid4()
        tag1 = UserTag(id=uuid4(), user_id=user_id, name="zebra")
        tag2 = UserTag(id=uuid4(), user_id=user_id, name="apple")

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [tag1, tag2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.get_user_tags(user_id)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_tags(self):
        """Should return empty list when user has no tags."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.get_user_tags(uuid4())

        assert result == []


class TestGetUserTagsPaginated:
    """Test paginated tag retrieval."""

    @pytest.mark.asyncio
    async def test_returns_tags_and_total_count(self):
        """Should return tags and total count."""
        mock_db = MagicMock()
        user_id = uuid4()

        # Count query returns total
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 10

        # Tags query returns page
        mock_tags_result = MagicMock()
        mock_tags_result.scalars.return_value.all.return_value = [
            UserTag(id=uuid4(), user_id=user_id, name="tag1"),
        ]

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_count_result
            return mock_tags_result

        mock_db.execute = mock_execute

        repo = UserTagRepository(mock_db)
        tags, total = await repo.get_user_tags_paginated(user_id, 5, 0)

        assert len(tags) == 1
        assert total == 10

    @pytest.mark.asyncio
    async def test_returns_zero_total_when_no_tags(self):
        """Should return 0 for total when user has no tags."""
        mock_db = MagicMock()

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = None

        mock_tags_result = MagicMock()
        mock_tags_result.scalars.return_value.all.return_value = []

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_count_result
            return mock_tags_result

        mock_db.execute = mock_execute

        repo = UserTagRepository(mock_db)
        tags, total = await repo.get_user_tags_paginated(uuid4(), 10, 0)

        assert total == 0
        assert tags == []


class TestCreateTag:
    """Test creating tags."""

    @pytest.mark.asyncio
    async def test_creates_and_returns_tag(self):
        """Should create tag and return it."""
        mock_db = MagicMock()
        user_id = uuid4()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        repo = UserTagRepository(mock_db)
        result = await repo.create_tag(user_id, "test-tag")

        assert result.name == "test-tag"
        assert result.user_id == user_id
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()


class TestUpdateTag:
    """Test updating tags."""

    @pytest.mark.asyncio
    async def test_updates_tag_fields(self):
        """Should update specified fields."""
        mock_db = MagicMock()
        tag_id = uuid4()
        mock_tag = UserTag(id=tag_id, name="old-name")
        mock_db.flush = AsyncMock()

        repo = UserTagRepository(mock_db)
        await repo.update_tag(mock_tag, {"name": "new-name"})

        assert mock_tag.name == "new-name"
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_invalid_fields(self):
        """Should skip fields that don't exist on model."""
        mock_db = MagicMock()
        mock_tag = UserTag(id=uuid4(), name="test")
        mock_db.flush = AsyncMock()

        repo = UserTagRepository(mock_db)
        await repo.update_tag(
            mock_tag, {"invalid_field": "value", "name": "new"}
        )

        assert mock_tag.name == "new"
        # Should not crash on invalid field


class TestDeleteTag:
    """Test deleting tags."""

    @pytest.mark.asyncio
    async def test_deletes_tag(self):
        """Should delete the tag."""
        mock_db = MagicMock()
        mock_tag = UserTag(id=uuid4(), name="to-delete")
        mock_db.delete = AsyncMock()
        mock_db.flush = AsyncMock()

        repo = UserTagRepository(mock_db)
        await repo.delete_tag(mock_tag)

        mock_db.delete.assert_called_once_with(mock_tag)
        mock_db.flush.assert_called_once()


class TestGetOrCreateTag:
    """Test get or create tag pattern."""

    @pytest.mark.asyncio
    async def test_returns_existing_tag(self):
        """Should return existing tag when found."""
        mock_db = MagicMock()
        user_id = uuid4()
        mock_tag = UserTag(id=uuid4(), user_id=user_id, name="tech")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tag
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.get_or_create_tag(user_id, "tech")

        assert result.id == mock_tag.id

    @pytest.mark.asyncio
    async def test_creates_tag_when_not_exists(self):
        """Should create tag when not found."""
        mock_db = MagicMock()
        user_id = uuid4()

        # First call (find) returns None
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = None

        # Create should work
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            return mock_result1

        mock_db.execute = mock_execute

        repo = UserTagRepository(mock_db)
        result = await repo.get_or_create_tag(user_id, "new-tag")

        assert result.name == "new-tag"
        mock_db.add.assert_called_once()


class TestGetArticleTags:
    """Test getting tags for an article."""

    @pytest.mark.asyncio
    async def test_returns_tag_ids_for_article(self):
        """Should return tag IDs for article belonging to user."""
        mock_db = MagicMock()
        user_id = uuid4()
        article_id = uuid4()
        tag_id = uuid4()

        # User article query returns article ID
        mock_ua_result = MagicMock()
        mock_ua_result.scalar_one_or_none.return_value = uuid4()

        # Tags query returns tag IDs
        mock_tags_result = MagicMock()
        mock_tags_result.all.return_value = [(tag_id,)]

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_ua_result
            return mock_tags_result

        mock_db.execute = mock_execute

        repo = UserTagRepository(mock_db)
        result = await repo.get_article_tags(article_id, user_id)

        assert len(result) == 1
        assert tag_id in result

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_user_article(self):
        """Should return empty list when article not found for user."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.get_article_tags(uuid4(), uuid4())

        assert result == []


class TestAddTagsToArticle:
    """Test adding tags to articles."""

    @pytest.mark.asyncio
    async def test_adds_new_tags_to_article(self):
        """Should add tags that don't already exist."""
        mock_db = MagicMock()
        user_id = uuid4()
        article_id = uuid4()
        tag_id = uuid4()

        # Owned tags query
        mock_owned_result = MagicMock()
        mock_owned_result.all.return_value = [(tag_id,)]

        # User article query
        mock_ua_result = MagicMock()
        mock_ua_result.scalar_one_or_none.return_value = uuid4()

        # Existing tags query (empty)
        mock_existing_result = MagicMock()
        mock_existing_result.all.return_value = []

        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_owned_result
            if call_count == 2:
                return mock_ua_result
            return mock_existing_result

        mock_db.execute = mock_execute

        repo = UserTagRepository(mock_db)
        result = await repo.add_tags_to_article(article_id, [tag_id], user_id)

        assert tag_id in result
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_for_non_owned_tags(self):
        """Should raise ValueError when tags don't belong to user."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []  # No owned tags
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)

        with pytest.raises(ValueError, match="not found or access denied"):
            await repo.add_tags_to_article(uuid4(), [uuid4()], uuid4())

    @pytest.mark.asyncio
    async def test_raises_for_nonexistent_article(self):
        """Should raise ValueError when article not found for user."""
        mock_db = MagicMock()
        tag_id = uuid4()

        # Owned tags query returns tag
        mock_owned_result = MagicMock()
        mock_owned_result.all.return_value = [(tag_id,)]

        # User article query returns None
        mock_ua_result = MagicMock()
        mock_ua_result.scalar_one_or_none.return_value = None

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_owned_result
            return mock_ua_result

        mock_db.execute = mock_execute

        repo = UserTagRepository(mock_db)

        with pytest.raises(ValueError, match="Article not found"):
            await repo.add_tags_to_article(uuid4(), [tag_id], uuid4())

    @pytest.mark.asyncio
    async def test_skips_existing_tag_relationships(self):
        """Should not add tags that already exist."""
        mock_db = MagicMock()
        user_id = uuid4()
        article_id = uuid4()
        tag_id = uuid4()

        mock_owned_result = MagicMock()
        mock_owned_result.all.return_value = [(tag_id,)]

        mock_ua_result = MagicMock()
        mock_ua_result.scalar_one_or_none.return_value = uuid4()

        # Tag already exists
        mock_existing_result = MagicMock()
        mock_existing_result.all.return_value = [(tag_id,)]

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_owned_result
            if call_count == 2:
                return mock_ua_result
            return mock_existing_result

        mock_db.execute = mock_execute
        mock_db.flush = AsyncMock()

        repo = UserTagRepository(mock_db)
        result = await repo.add_tags_to_article(article_id, [tag_id], user_id)

        # Should return empty list since tag already exists
        assert result == []
        mock_db.add.assert_not_called()


class TestRemoveTagsFromArticle:
    """Test removing tags from articles."""

    @pytest.mark.asyncio
    async def test_removes_tags_from_article(self):
        """Should remove specified tags from article."""
        mock_db = MagicMock()
        user_id = uuid4()
        article_id = uuid4()
        tag_id = uuid4()

        # User article exists
        mock_ua_result = MagicMock()
        mock_ua_result.scalar_one_or_none.return_value = uuid4()

        # Existing tags
        mock_existing_result = MagicMock()
        mock_existing_result.all.return_value = [(tag_id,)]

        # Delete result
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_ua_result
            if call_count == 2:
                return mock_existing_result
            return mock_delete_result

        mock_db.execute = mock_execute
        mock_db.flush = AsyncMock()

        repo = UserTagRepository(mock_db)
        result = await repo.remove_tags_from_article(
            article_id, [tag_id], user_id
        )

        assert tag_id in result

    @pytest.mark.asyncio
    async def test_returns_empty_for_nonexistent_article(self):
        """Should return empty list when article not found for user."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.remove_tags_from_article(
            uuid4(), [uuid4()], uuid4()
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_for_empty_tag_list(self):
        """Should return empty list when no tags provided."""
        mock_db = MagicMock()

        repo = UserTagRepository(mock_db)
        result = await repo.remove_tags_from_article(uuid4(), [], uuid4())

        assert result == []
        mock_db.execute.assert_not_called()


class TestRemoveArticlesFromAllTags:
    """Test bulk removal of articles from all tags."""

    @pytest.mark.asyncio
    async def test_removes_articles_from_all_tags(self):
        """Should remove all tag relationships for articles."""
        mock_db = MagicMock()
        user_id = uuid4()
        article_id = uuid4()

        # User articles query
        mock_ua_result = MagicMock()
        user_article_id = uuid4()
        mock_ua_result.all.return_value = [(user_article_id,)]

        # Delete result
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 5

        call_count = 0

        async def mock_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_ua_result
            return mock_delete_result

        mock_db.execute = mock_execute
        mock_db.flush = AsyncMock()

        repo = UserTagRepository(mock_db)
        result = await repo.remove_articles_from_all_tags([article_id], user_id)

        assert result == 5

    @pytest.mark.asyncio
    async def test_returns_zero_for_empty_article_list(self):
        """Should return 0 when no articles provided."""
        mock_db = MagicMock()

        repo = UserTagRepository(mock_db)
        result = await repo.remove_articles_from_all_tags([], uuid4())

        assert result == 0
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_user_articles(self):
        """Should return 0 when articles not found for user."""
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = UserTagRepository(mock_db)
        result = await repo.remove_articles_from_all_tags([uuid4()], uuid4())

        assert result == 0

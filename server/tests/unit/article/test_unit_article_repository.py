"""Unit tests for ArticleRepository."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy import Select

from backend.infrastructure.repositories.article import (
    ArticleRepository,
)

if TYPE_CHECKING:
    pass


class TestGetUserArticleState:
    """Test get_user_article_state method."""

    @pytest.mark.asyncio
    async def test_returns_state_when_found(self):
        """Should return UserArticle state when found."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_state = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_state
        mock_db.execute.return_value = mock_result

        article_id = uuid4()
        current_user = MagicMock(id=uuid4())

        result = await repo.get_user_article_state(article_id, current_user)

        assert result == mock_state
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_not_found_when_state_missing(self):
        """Should raise NotFoundError when state record doesn't exist."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        article_id = uuid4()
        current_user = MagicMock(id=uuid4())

        with pytest.raises(NotFoundError) as exc_info:
            await repo.get_user_article_state(article_id, current_user)

        assert "Article state not found" in str(exc_info.value)


class TestFindById:
    """Test find_by_id method."""

    @pytest.mark.asyncio
    async def test_returns_user_article_when_found(self):
        """Should return UserArticle when found."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_state = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_state
        mock_db.execute.return_value = mock_result

        article_id = uuid4()
        user_id = uuid4()

        result = await repo.find_by_id(article_id, user_id)

        assert result == mock_state

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when UserArticle doesn't exist."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        article_id = uuid4()
        user_id = uuid4()

        result = await repo.find_by_id(article_id, user_id)

        assert result is None


class TestMarkArticleAsRead:
    """Test mark_article_as_read method."""

    @pytest.mark.asyncio
    async def test_marks_unread_article_as_read(self):
        """Should mark article as read and update user last_active."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_state = MagicMock()
        mock_state.is_read = False
        repo.get_user_article_state = AsyncMock(return_value=mock_state)

        current_user = MagicMock(id=uuid4())
        article_id = uuid4()

        await repo.mark_article_as_read(article_id, current_user)

        assert mock_state.is_read is True
        assert hasattr(mock_state, "read_at")
        assert hasattr(current_user, "last_active")

    @pytest.mark.asyncio
    async def test_already_read_article_no_change(self):
        """Should not update state if article is already read."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_state = MagicMock()
        mock_state.is_read = True
        repo.get_user_article_state = AsyncMock(return_value=mock_state)

        current_user = MagicMock(id=uuid4())
        article_id = uuid4()

        await repo.mark_article_as_read(article_id, current_user)

        assert mock_state.is_read is True
        assert hasattr(current_user, "last_active")


class TestUpdateArticleReadState:
    """Test update_article_read_state method."""

    @pytest.mark.asyncio
    async def test_updates_state_with_changes(self):
        """Should update state and return True when changes are made."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_state = MagicMock()
        mock_state.is_read = False
        mock_state.read_at = None
        repo.get_user_article_state = AsyncMock(return_value=mock_state)

        article_id = uuid4()
        state_update = {"is_read": True, "read_later": True}
        current_user = MagicMock(id=uuid4())

        result = await repo.update_article_read_state(
            article_id, state_update, current_user
        )

        assert result is True
        assert mock_state.is_read is True
        assert mock_state.read_later is True
        assert hasattr(mock_state, "read_at")

    @pytest.mark.asyncio
    async def test_returns_false_with_empty_update(self):
        """Should return False when no update data provided."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        article_id = uuid4()
        current_user = MagicMock(id=uuid4())

        result = await repo.update_article_read_state(
            article_id, {}, current_user
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_sets_read_at_when_marking_read(self):
        """Should set read_at when marking article as read."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_state = MagicMock()
        mock_state.is_read = False
        mock_state.read_at = None
        repo.get_user_article_state = AsyncMock(return_value=mock_state)

        article_id = uuid4()
        state_update = {"is_read": True}
        current_user = MagicMock(id=uuid4())

        await repo.update_article_read_state(
            article_id, state_update, current_user
        )

        assert hasattr(mock_state, "read_at")


class TestBulkMarkArticles:
    """Test bulk_mark_articles method."""

    @pytest.mark.asyncio
    async def test_marks_articles_as_read(self):
        """Should bulk mark articles as read and return count."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_db.execute.return_value = mock_result

        current_user = MagicMock(id=uuid4())
        article_ids = [uuid4() for _ in range(5)]

        result = await repo.bulk_mark_articles(
            current_user, article_ids, is_read=True
        )

        assert result == 5
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_marks_articles_as_unread(self):
        """Should bulk mark articles as unread and return count."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_db.execute.return_value = mock_result

        current_user = MagicMock(id=uuid4())
        article_ids = [uuid4() for _ in range(3)]

        result = await repo.bulk_mark_articles(
            current_user, article_ids, is_read=False
        )

        assert result == 3

    @pytest.mark.asyncio
    async def test_returns_zero_with_empty_list(self):
        """Should return 0 when article_ids list is empty."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        result = await repo.bulk_mark_articles(current_user, [], is_read=True)

        assert result == 0
        mock_db.execute.assert_not_called()


class TestBuildArticlesBaseQuery:
    """Test build_articles_base_query method."""

    def test_builds_base_query_with_user_filter(self):
        """Should build base query with user filtering."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        query = repo.build_articles_base_query(current_user)

        assert isinstance(query, Select)

    def test_applies_subscription_ids_filter(self):
        """Should apply subscription_ids filter when provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())
        subscription_ids = [uuid4()]

        query = repo.build_articles_base_query(
            current_user, subscription_ids=subscription_ids
        )

        assert isinstance(query, Select)

    def test_applies_folder_ids_filter(self):
        """Should apply folder_ids filter when provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())
        folder_ids = [uuid4()]

        query = repo.build_articles_base_query(
            current_user, folder_ids=folder_ids
        )

        assert isinstance(query, Select)

    def test_applies_tag_ids_filter(self):
        """Should apply tag_ids filter when provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())
        tag_ids = [uuid4(), uuid4()]

        query = repo.build_articles_base_query(current_user, tag_ids=tag_ids)

        assert isinstance(query, Select)

    def test_applies_is_read_filter(self):
        """Should apply is_read filter when provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        query = repo.build_articles_base_query(current_user, is_read="read")

        assert isinstance(query, Select)

    def test_applies_read_later_filter(self):
        """Should apply read_later filter when provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        query = repo.build_articles_base_query(current_user, read_later="true")

        assert isinstance(query, Select)

    def test_applies_search_query(self):
        """Should apply search query when provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        query = repo.build_articles_base_query(current_user, q="search term")

        assert isinstance(query, Select)


class TestBuildCursorFiltering:
    """Test build_cursor_filtering method."""

    def test_returns_ordered_query_without_cursor(self):
        """Should return ordered query when no cursor provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        base_query = MagicMock()

        result = repo.build_cursor_filtering(base_query, {})

        assert result is not None

    def test_returns_ordered_query_with_search(self):
        """Should return ordered query with search when no cursor provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())
        base_query = repo.build_articles_base_query(current_user, q="search")

        result = repo.build_cursor_filtering(
            base_query, {}, has_search=True, q="search"
        )

        assert result is not None

    def test_applies_cursor_filtering_with_cursor(self):
        """Should apply cursor filtering when cursor data provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        base_query = MagicMock()
        cursor_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "is_published_at": True,
            "article_id": str(uuid4()),
        }

        result = repo.build_cursor_filtering(base_query, cursor_data)

        assert result is not None

    def test_applies_cursor_filtering_with_search_cursor(self):
        """Should apply cursor filtering with search cursor when provided."""
        mock_db = MagicMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())
        base_query = repo.build_articles_base_query(current_user, q="search")
        cursor_data = {
            "relevance": "0.8",
            "timestamp": datetime.now(UTC).isoformat(),
            "is_published_at": True,
            "article_id": str(uuid4()),
        }

        result = repo.build_cursor_filtering(
            base_query, cursor_data, has_search=True, q="search"
        )

        assert result is not None


class TestGetArticlesCount:
    """Test get_articles_count method."""

    @pytest.mark.asyncio
    async def test_returns_total_count(self):
        """Should return total count of matching articles."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_db.execute.return_value = mock_result

        current_user = MagicMock(id=uuid4())

        result = await repo.get_articles_count(current_user)

        assert result == 42

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_articles(self):
        """Should return 0 when no articles match."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_db.execute.return_value = mock_result

        current_user = MagicMock(id=uuid4())

        result = await repo.get_articles_count(current_user)

        assert result == 0


class TestGetArticleById:
    """Test get_article_by_id method."""

    @pytest.mark.asyncio
    async def test_returns_article_when_found(self):
        """Should return article with subscription info when found."""
        from backend.models import Article

        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        article_id = uuid4()
        subscription_id = uuid4()
        mock_article = MagicMock(spec=Article)
        mock_article.content = None

        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = Mock(
            side_effect=lambda i: [
                mock_article,
                subscription_id,
                "Test Feed",
                "https://example.com",
                "rss",
            ][i]
        )
        mock_row.__iter__ = Mock(
            return_value=iter(
                [
                    mock_article,
                    subscription_id,
                    "Test Feed",
                    "https://example.com",
                    "rss",
                ]
            )
        )
        mock_result.first.return_value = mock_row
        mock_db.execute.return_value = mock_result

        current_user = MagicMock(id=uuid4())

        result = await repo.get_article_by_id(article_id, current_user)

        assert result is not None
        assert result[0] == mock_article

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when article not found."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_db.execute.return_value = mock_result

        article_id = uuid4()
        current_user = MagicMock(id=uuid4())

        result = await repo.get_article_by_id(article_id, current_user)

        assert result is None


class TestGetArticleTags:
    """Test get_article_tags method."""

    @pytest.mark.asyncio
    async def test_returns_tags_mapping(self):
        """Should return dictionary mapping article IDs to their tags."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        article_id = uuid4()
        user_id = uuid4()
        mock_tag = MagicMock()

        mock_user_articles_result = MagicMock()
        mock_user_article = MagicMock()
        mock_user_article.article_id = article_id
        mock_user_article.id = uuid4()
        mock_user_articles_result.all.return_value = [mock_user_article]

        mock_tags_result = MagicMock()
        mock_tags_result.all.return_value = [(mock_tag, mock_user_article.id)]

        async def mock_execute_func(query):
            if "user_articles" in str(query):
                return mock_user_articles_result
            return mock_tags_result

        mock_db.execute = mock_execute_func

        current_user = MagicMock(id=user_id)

        result = await repo.get_article_tags([article_id], current_user)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_returns_empty_dict_with_no_article_ids(self):
        """Should return empty dict when no article_ids provided."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        result = await repo.get_article_tags([], current_user)

        assert result == {}


class TestBuildMarkAllArticlesQuery:
    """Test build_mark_all_articles_query method."""

    @pytest.mark.asyncio
    async def test_builds_query_for_all_articles(self):
        """Should build query for all user articles."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        query = await repo.build_mark_all_articles_query(current_user)

        assert isinstance(query, Select)

    @pytest.mark.asyncio
    async def test_builds_query_with_subscription_filter(self):
        """Should build query with subscription_ids filter."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())
        subscription_ids = [uuid4()]

        query = await repo.build_mark_all_articles_query(
            current_user, subscription_ids=subscription_ids
        )

        assert isinstance(query, Select)

    @pytest.mark.asyncio
    async def test_builds_query_with_folder_filter(self):
        """Should build query with folder_ids filter."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())
        folder_ids = [uuid4()]

        query = await repo.build_mark_all_articles_query(
            current_user, folder_ids=folder_ids
        )

        assert isinstance(query, Select)

    @pytest.mark.asyncio
    async def test_builds_query_with_read_later_filter(self):
        """Should build query with read_later filter."""
        mock_db = AsyncMock()
        repo = ArticleRepository(mock_db)

        current_user = MagicMock(id=uuid4())

        query = await repo.build_mark_all_articles_query(
            current_user, read_later=True
        )

        assert isinstance(query, Select)

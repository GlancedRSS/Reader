"""Unit tests for ArticleApplication."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.application.article.article import ArticleApplication
from backend.models import User

if TYPE_CHECKING:
    pass


class TestGetArticles:
    """Test get_articles method."""

    @pytest.mark.asyncio
    async def test_get_articles_success(self):
        """Should return paginated articles successfully."""
        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)

        mock_articles_query_result = MagicMock()
        mock_articles_query_result.articles = [
            MagicMock(
                id=uuid4(),
                title="Test Article",
                media_url="https://example.com/image.jpg",
                published_at=datetime.now(UTC),
                summary="Test summary",
            )
        ]
        mock_articles_query_result.metadata = {
            uuid4(): MagicMock(
                subscription_id=uuid4(),
                subscription_title="Test Feed",
                subscription_website="https://example.com",
                feed_type="rss",
                is_read=False,
                read_later=False,
            )
        }
        mock_articles_query_result.has_more = False
        mock_articles_query_result.next_cursor = None

        app.repository.build_articles_base_query = MagicMock()
        app.repository.build_cursor_filtering = MagicMock()
        app.repository.execute_articles_query = AsyncMock(
            return_value=mock_articles_query_result
        )
        app.repository.get_articles_count = AsyncMock(return_value=1)
        app.repository.get_article_tags = AsyncMock(return_value={})

        result = await app.get_articles(current_user)

        assert result.data is not None
        assert result.pagination.total == 1

    @pytest.mark.asyncio
    async def test_get_articles_with_folder_validation_error(self):
        """Should raise NotFoundError when folder not found."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        folder_ids = [uuid4()]

        app.folder_repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await app.get_articles(current_user, folder_ids=folder_ids)

        assert "Folder not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_articles_with_subscription_validation_error(self):
        """Should raise NotFoundError when subscription not found."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        subscription_ids = [uuid4()]

        app.user_feed_repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await app.get_articles(
                current_user, subscription_ids=subscription_ids
            )

        assert "Subscription not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_articles_with_tag_validation_error(self):
        """Should raise NotFoundError when tag not found."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        tag_ids = [uuid4()]

        app.user_tag_repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await app.get_articles(current_user, tag_ids=tag_ids)

        assert "One or more tags not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_articles_with_search_query(self):
        """Should successfully search articles with query."""
        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)

        mock_articles_query_result = MagicMock()
        mock_articles_query_result.articles = [
            MagicMock(
                id=uuid4(),
                title="Test Article",
                media_url="https://example.com/image.jpg",
                published_at=datetime.now(UTC),
                summary="Test summary",
            )
        ]
        mock_articles_query_result.metadata = {
            uuid4(): MagicMock(
                subscription_id=uuid4(),
                subscription_title="Test Feed",
                subscription_website="https://example.com",
                feed_type="rss",
                is_read=False,
                read_later=False,
                relevance=0.8,
            )
        }
        mock_articles_query_result.has_more = False
        mock_articles_query_result.next_cursor = None

        app.repository.build_articles_base_query = MagicMock()
        app.repository.build_cursor_filtering = MagicMock()
        app.repository.execute_articles_query = AsyncMock(
            return_value=mock_articles_query_result
        )
        app.repository.get_articles_count = AsyncMock(return_value=1)
        app.repository.get_article_tags = AsyncMock(return_value={})

        result = await app.get_articles(current_user, q="search term")

        assert result.data is not None
        assert result.pagination.total == 1

    @pytest.mark.asyncio
    async def test_get_articles_with_multiple_filters(self):
        """Should successfully handle multiple filters (no longer raises error)."""
        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)

        mock_articles_query_result = MagicMock()
        mock_articles_query_result.articles = []
        mock_articles_query_result.metadata = {}
        mock_articles_query_result.has_more = False
        mock_articles_query_result.next_cursor = None

        app.repository.build_articles_base_query = MagicMock()
        app.repository.build_cursor_filtering = MagicMock()
        app.repository.execute_articles_query = AsyncMock(
            return_value=mock_articles_query_result
        )
        app.repository.get_articles_count = AsyncMock(return_value=0)
        app.repository.get_article_tags = AsyncMock(return_value={})

        # Mock the repository find methods to return values
        app.folder_repository.find_by_id = AsyncMock(return_value=MagicMock())
        app.user_feed_repository.find_by_id = AsyncMock(
            return_value=MagicMock()
        )

        # This should NOT raise ValidationError anymore
        result = await app.get_articles(
            current_user,
            subscription_ids=[uuid4()],
            folder_ids=[uuid4()],
        )

        assert result.data is not None


class TestGetArticle:
    """Test get_article method."""

    @pytest.mark.asyncio
    async def test_get_article_success(self):
        """Should return article details and mark as read."""
        from backend.models import Article

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        article_id = uuid4()
        subscription_id = uuid4()
        current_user = MagicMock(id=uuid4(), spec=User)

        mock_article = MagicMock(spec=Article)
        mock_article.id = article_id
        mock_article.title = "Test Article"
        mock_article.summary = "Test summary"
        mock_article.content = None
        mock_article.canonical_url = "https://example.com/article"
        mock_article.author = "Test Author"
        mock_article.media_url = None
        mock_article.platform_metadata = {}

        app.repository.get_article_by_id = AsyncMock(
            return_value=(
                mock_article,
                subscription_id,
                "Test Feed",
                "https://example.com",
            )
        )
        app.repository.mark_article_as_read = AsyncMock()
        app.repository.get_user_article_state = AsyncMock(
            return_value=MagicMock(
                is_read=False,
                read_later=False,
            )
        )
        app.repository.get_article_tags = AsyncMock(return_value={})

        result = await app.get_article(article_id, current_user)

        assert result is not None
        assert result.title == "Test Article"

    @pytest.mark.asyncio
    async def test_get_article_not_found(self):
        """Should raise NotFoundError when article doesn't exist."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        article_id = uuid4()
        current_user = MagicMock(id=uuid4(), spec=User)

        app.repository.get_article_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await app.get_article(article_id, current_user)

        assert "Article not found" in str(exc_info.value)


class TestUpdateArticleState:
    """Test update_article_state method."""

    @pytest.mark.asyncio
    async def test_update_state_success(self):
        """Should update article state successfully."""
        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        article_id = uuid4()
        current_user = MagicMock(id=uuid4(), spec=User)

        state_data = MagicMock()
        state_data.model_dump = MagicMock(return_value={"is_read": True})
        state_data.tag_ids = None

        app.repository.find_by_id = AsyncMock(return_value=MagicMock())
        app.repository.update_article_read_state = AsyncMock(return_value=True)
        app._update_article_tags = AsyncMock()

        result = await app.update_article_state(
            article_id, state_data, current_user
        )

        assert result.message == "Article updated successfully"

    @pytest.mark.asyncio
    async def test_update_state_article_not_found(self):
        """Should raise NotFoundError when article doesn't exist."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        article_id = uuid4()
        current_user = MagicMock(id=uuid4(), spec=User)

        state_data = MagicMock()

        app.repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await app.update_article_state(article_id, state_data, current_user)

        assert "Article not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_state_with_tags(self):
        """Should update article tags when tag_ids provided."""
        mock_db = AsyncMock()
        mock_tag_app = AsyncMock()
        app = ArticleApplication(mock_db, tag_management=mock_tag_app)

        article_id = uuid4()
        current_user = MagicMock(id=uuid4(), spec=User)

        state_data = MagicMock()
        state_data.model_dump = MagicMock(return_value={})
        state_data.tag_ids = [uuid4(), uuid4()]

        app.repository.find_by_id = AsyncMock(return_value=MagicMock())
        app.repository.update_article_read_state = AsyncMock(return_value=False)
        app.tag_management.sync_article_tags = AsyncMock()

        await app.update_article_state(article_id, state_data, current_user)

        app.tag_management.sync_article_tags.assert_called_once()


class TestMarkAllAsRead:
    """Test mark_all_as_read method."""

    @pytest.mark.asyncio
    async def test_mark_all_as_read_success(self):
        """Should mark all articles as read successfully."""
        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)

        request_data = MagicMock()
        request_data.subscription_ids = None
        request_data.folder_ids = None
        request_data.tag_ids = None
        request_data.is_read_filter = None
        request_data.read_later = None
        request_data.q = None
        request_data.from_date = None
        request_data.to_date = None
        request_data.is_read = True

        app.repository.build_mark_all_articles_query = AsyncMock(
            return_value=MagicMock()
        )
        app.repository.bulk_mark_articles = AsyncMock(return_value=5)

        result = await app.mark_all_as_read(request_data, current_user)

        assert "marked" in result.message.lower()

    @pytest.mark.asyncio
    async def test_mark_all_as_read_with_subscription_validation_error(self):
        """Should raise NotFoundError when subscription not found."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)

        request_data = MagicMock()
        request_data.subscription_ids = [uuid4()]
        request_data.folder_ids = None
        request_data.tag_ids = None
        request_data.is_read_filter = None
        request_data.read_later = None
        request_data.q = None
        request_data.from_date = None
        request_data.to_date = None
        request_data.is_read = True

        app.user_feed_repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await app.mark_all_as_read(request_data, current_user)

        assert "Subscription not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_mark_all_as_read_with_folder_validation_error(self):
        """Should raise NotFoundError when folder not found."""
        from backend.core.exceptions import NotFoundError

        mock_db = AsyncMock()
        app = ArticleApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)

        request_data = MagicMock()
        request_data.subscription_ids = None
        request_data.folder_ids = [uuid4()]
        request_data.tag_ids = None
        request_data.is_read_filter = None
        request_data.read_later = None
        request_data.q = None
        request_data.from_date = None
        request_data.to_date = None
        request_data.is_read = True

        app.folder_repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            await app.mark_all_as_read(request_data, current_user)

        assert "Folder not found" in str(exc_info.value)


class TestUpdateArticleTags:
    """Test _update_article_tags method."""

    @pytest.mark.asyncio
    async def test_returns_early_when_tag_ids_is_none(self):
        """Should return early without updating when tag_ids is None."""
        mock_db = AsyncMock()
        mock_tag_app = AsyncMock()
        app = ArticleApplication(mock_db, tag_management=mock_tag_app)

        article_id = uuid4()
        current_user = MagicMock(id=uuid4(), spec=User)

        state_data = MagicMock()
        state_data.tag_ids = None

        await app._update_article_tags(article_id, state_data, current_user)

        app.tag_management.sync_article_tags.assert_not_called()

    @pytest.mark.asyncio
    async def test_syncs_tags_when_tag_ids_provided(self):
        """Should sync article tags when tag_ids is provided."""
        mock_db = AsyncMock()
        mock_tag_app = AsyncMock()
        app = ArticleApplication(mock_db, tag_management=mock_tag_app)

        article_id = uuid4()
        current_user = MagicMock(id=uuid4(), spec=User)

        state_data = MagicMock()
        state_data.tag_ids = [uuid4(), uuid4()]

        app.tag_management.sync_article_tags = AsyncMock()

        await app._update_article_tags(article_id, state_data, current_user)

        app.tag_management.sync_article_tags.assert_called_once_with(
            current_user.id, article_id, state_data.tag_ids
        )


class TestBuildArticleListResponse:
    """Test _build_article_list_response method."""

    def test_builds_response_with_articles(self):
        """Should build article list response from raw data."""
        mock_db = MagicMock()
        app = ArticleApplication(mock_db)

        article_id = uuid4()
        subscription_id = uuid4()

        articles = [
            MagicMock(
                id=article_id,
                title="Test Article",
                media_url="https://example.com/image.jpg",
                published_at=datetime.now(UTC),
                summary="Test summary",
            )
        ]

        metadata = {
            article_id: MagicMock(
                subscription_id=subscription_id,
                subscription_title="Test Feed",
                subscription_website="https://example.com",
                feed_type="rss",
                is_read=False,
                read_later=False,
            )
        }

        tags_by_article = {}

        result = app._build_article_list_response(
            articles, metadata, tags_by_article
        )

        assert len(result) == 1
        assert result[0].title == "Test Article"


class TestBuildArticleResponse:
    """Test _build_article_response method."""

    def test_builds_single_article_response(self):
        """Should build single article response."""
        from backend.models import Article

        mock_db = MagicMock()
        app = ArticleApplication(mock_db)

        article_id = uuid4()
        subscription_id = uuid4()

        mock_article = MagicMock(spec=Article)
        mock_article.id = article_id
        mock_article.title = "Test Article"
        mock_article.summary = "Test summary"
        mock_article.content = None
        mock_article.canonical_url = "https://example.com/article"
        mock_article.author = "Test Author"
        mock_article.media_url = None
        mock_article.platform_metadata = {}

        state = MagicMock()
        state.is_read = False
        state.read_later = False

        article_tags = []

        result = app._build_article_response(
            article=mock_article,
            subscription_id=subscription_id,
            subscription_title="Test Feed",
            subscription_website="https://example.com",
            state=state,
            article_tags=article_tags,
        )

        assert result.title == "Test Article"
        assert result.is_read is False


class TestBuildPaginatedResponse:
    """Test _build_paginated_response method."""

    def test_builds_paginated_response_with_has_more(self):
        """Should build paginated response with has_more computed."""
        mock_db = MagicMock()
        app = ArticleApplication(mock_db)

        data = [{"id": 1}, {"id": 2}]
        total = 10
        limit = 2

        result = app._build_paginated_response(data, total, limit)

        assert result.data == data
        assert result.pagination.total == total
        assert result.pagination.has_more is True

    def test_builds_paginated_response_with_explicit_has_more(self):
        """Should build paginated response with explicit has_more."""
        mock_db = MagicMock()
        app = ArticleApplication(mock_db)

        data = [{"id": 1}]
        total = 1
        limit = 10

        result = app._build_paginated_response(
            data, total, limit, has_more=False
        )

        assert result.pagination.has_more is False

    def test_builds_paginated_response_with_next_cursor(self):
        """Should build paginated response with next_cursor."""
        mock_db = MagicMock()
        app = ArticleApplication(mock_db)

        data = [{"id": 1}]
        total = 10
        limit = 1
        next_cursor = "next_page_token"

        result = app._build_paginated_response(
            data, total, limit, next_cursor=next_cursor
        )

        assert result.pagination.next_cursor == next_cursor

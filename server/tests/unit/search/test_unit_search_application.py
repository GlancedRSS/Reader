"""Unit tests for SearchApplication."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.application.search.search import SearchApplication
from backend.models import User
from backend.schemas.domain import (
    ArticleListResponse,
    FeedSearchRequest,
    UnifiedSearchRequest,
)


class TestUniversalSearch:
    """Test universal_search method."""

    @pytest.mark.asyncio
    async def test_universal_search_aggregates_results(self):
        """Should aggregate results from all search types with type weights."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        query = "test query"
        current_user = MagicMock(id=uuid4(), spec=User)
        request = UnifiedSearchRequest(query=query)

        # Mock search methods to return sample data
        app._search_articles_with_score = AsyncMock(
            return_value=[
                {
                    "type": "articles",
                    "score": 0.8,
                    "id": uuid4(),
                    "title": "Test Article",
                    "data": {
                        "id": uuid4(),
                        "title": "Test Article",
                        "summary": "Test",
                    },
                }
            ]
        )
        app._search_feeds_with_score = AsyncMock(return_value=[])
        app._search_tags_with_score = AsyncMock(return_value=[])
        app._search_folders_with_score = AsyncMock(return_value=[])

        result = await app.universal_search(request, current_user)

        assert len(result.data) == 1
        assert result.data[0].type == "article"

    @pytest.mark.asyncio
    async def test_universal_search_weights_results_by_type(self):
        """Should apply type weights when ranking results."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        request = UnifiedSearchRequest(query="test")

        # Mock different types with same base score
        article_id = uuid4()
        feed_id = uuid4()
        uuid4()

        app._search_articles_with_score = AsyncMock(
            return_value=[
                {
                    "type": "articles",
                    "score": 0.5,
                    "id": article_id,
                    "title": "Article",
                    "data": {
                        "id": article_id,
                        "title": "Article",
                        "summary": "Test",
                    },
                }
            ]
        )
        app._search_feeds_with_score = AsyncMock(
            return_value=[
                {
                    "type": "feeds",
                    "score": 0.5,
                    "id": feed_id,
                    "title": "Feed",
                    "data": {
                        "id": feed_id,
                        "title": "Feed",
                        "website": "https://example.com",
                        "is_active": True,
                        "is_pinned": False,
                        "unread_count": 5,
                    },
                }
            ]
        )
        app._search_tags_with_score = AsyncMock(return_value=[])
        app._search_folders_with_score = AsyncMock(return_value=[])

        result = await app.universal_search(request, current_user)

        # Feed weight (2.0) > Article weight (1.8), so feed should rank higher
        assert len(result.data) == 2
        assert result.data[0].type == "feed"
        assert result.data[1].type == "article"

    @pytest.mark.asyncio
    async def test_universal_search_limits_to_20_results(self):
        """Should return maximum 20 results regardless of input size."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        request = UnifiedSearchRequest(query="test")

        # Mock 25 results total (15 articles, 10 feeds)
        app._search_articles_with_score = AsyncMock(
            return_value=[
                {
                    "type": "articles",
                    "score": 0.5,
                    "id": uuid4(),
                    "title": f"Article {i}",
                    "data": {
                        "id": uuid4(),
                        "title": f"Article {i}",
                        "summary": "Test",
                    },
                }
                for i in range(15)
            ]
        )
        app._search_feeds_with_score = AsyncMock(
            return_value=[
                {
                    "type": "feeds",
                    "score": 0.5,
                    "id": uuid4(),
                    "title": f"Feed {i}",
                    "data": {
                        "id": uuid4(),
                        "title": f"Feed {i}",
                        "website": "https://example.com",
                        "is_active": True,
                        "is_pinned": False,
                        "unread_count": 5,
                    },
                }
                for i in range(10)
            ]
        )
        app._search_tags_with_score = AsyncMock(return_value=[])
        app._search_folders_with_score = AsyncMock(return_value=[])

        result = await app.universal_search(request, current_user)

        assert len(result.data) == 20

    @pytest.mark.asyncio
    async def test_universal_search_handles_exceptions_gracefully(self):
        """Should continue when individual search types fail."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        request = UnifiedSearchRequest(query="test")

        article_id = uuid4()

        # Mock articles to succeed, feeds to raise exception
        app._search_articles_with_score = AsyncMock(
            return_value=[
                {
                    "type": "articles",
                    "score": 0.5,
                    "id": article_id,
                    "title": "Article",
                    "data": {
                        "id": article_id,
                        "title": "Article",
                        "summary": "Test",
                    },
                }
            ]
        )
        app._search_feeds_with_score = AsyncMock(
            side_effect=Exception("Search failed")
        )
        app._search_tags_with_score = AsyncMock(return_value=[])
        app._search_folders_with_score = AsyncMock(return_value=[])

        result = await app.universal_search(request, current_user)

        # Should still return articles result
        assert len(result.data) == 1
        assert result.data[0].type == "article"


class TestSearchFeeds:
    """Test search_feeds method."""

    @pytest.mark.asyncio
    async def test_search_feeds_success(self):
        """Should return feed search results."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        feed_id = uuid4()

        mock_result = {
            "data": [
                {
                    "id": feed_id,
                    "title": "Test Feed",
                    "website": "https://example.com",
                    "is_active": True,
                    "is_pinned": False,
                    "unread_count": 5,
                    "_relevance": 0.8,
                }
            ],
            "pagination": {
                "total": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False,
            },
        }

        app.repository.search_feeds = AsyncMock(return_value=mock_result)

        request = FeedSearchRequest(query="test")
        result = await app.search_feeds(request, current_user)

        assert len(result.data) == 1
        assert result.data[0].title == "Test Feed"


class TestSearchTags:
    """Test search_tags method."""

    @pytest.mark.asyncio
    async def test_search_tags_success(self):
        """Should return tag search results."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        tag_id = uuid4()

        mock_result = {
            "data": [
                {
                    "id": tag_id,
                    "name": "test-tag",
                    "article_count": 10,
                    "_relevance": 0.9,
                }
            ],
            "pagination": {
                "total": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False,
            },
        }

        app.repository.search_tags = AsyncMock(return_value=mock_result)

        from backend.schemas.domain import TagSearchRequest

        request = TagSearchRequest(query="test")
        result = await app.search_tags(request, current_user)

        assert len(result.data) == 1
        assert result.data[0].name == "test-tag"
        assert result.data[0].article_count == 10


class TestSearchFolders:
    """Test search_folders method."""

    @pytest.mark.asyncio
    async def test_search_folders_success(self):
        """Should return folder search results."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        current_user = MagicMock(id=uuid4(), spec=User)
        folder_id = uuid4()

        mock_result = {
            "data": [
                {
                    "id": folder_id,
                    "name": "Tech",
                    "unread_count": 15,
                    "is_pinned": True,
                    "_relevance": 0.7,
                }
            ],
            "pagination": {
                "total": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False,
            },
        }

        app.repository.search_folders = AsyncMock(return_value=mock_result)

        from backend.schemas.domain import FolderSearchRequest

        request = FolderSearchRequest(query="tech")
        result = await app.search_folders(request, current_user)

        assert len(result.data) == 1
        assert result.data[0].name == "Tech"
        assert result.data[0].unread_count == 15
        assert result.data[0].is_pinned is True


class TestSearchHelpersWithScores:
    """Test internal search helper methods."""

    @pytest.mark.asyncio
    async def test_search_articles_with_score_normalizes_scores(self):
        """Should normalize article scores using ArticleRepository."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        user_id = uuid4()

        # Mock ArticleRepository methods
        from collections import namedtuple
        from unittest.mock import patch

        from backend.infrastructure.repositories.article import (
            ArticleMetadata,
            ArticleRepository,
            ArticlesQueryResult,
        )

        ArticleRow = namedtuple(
            "ArticleRow",
            [
                "id",
                "title",
                "media_url",
                "published_at",
                "summary",
                "canonical_url",
                "author",
                "created_at",
            ],
        )

        article_ids = [uuid4() for _ in range(3)]
        subscription_id = uuid4()

        articles = [
            ArticleRow(
                id=article_ids[0],
                title="Article 1",
                media_url=None,
                published_at=None,
                summary="Test",
                canonical_url=None,
                author=None,
                created_at=None,
            ),
            ArticleRow(
                id=article_ids[1],
                title="Article 2",
                media_url=None,
                published_at=None,
                summary="Test",
                canonical_url=None,
                author=None,
                created_at=None,
            ),
            ArticleRow(
                id=article_ids[2],
                title="Article 3",
                media_url=None,
                published_at=None,
                summary="Test",
                canonical_url=None,
                author=None,
                created_at=None,
            ),
        ]

        metadata = {
            article_ids[0]: ArticleMetadata(
                subscription_id=subscription_id,
                subscription_title="Test Feed",
                subscription_website="https://example.com",
                is_read=False,
                read_later=False,
                relevance=0.5,
            ),
            article_ids[1]: ArticleMetadata(
                subscription_id=subscription_id,
                subscription_title="Test Feed",
                subscription_website="https://example.com",
                is_read=False,
                read_later=False,
                relevance=0.8,
            ),
            article_ids[2]: ArticleMetadata(
                subscription_id=subscription_id,
                subscription_title="Test Feed",
                subscription_website="https://example.com",
                is_read=False,
                read_later=False,
                relevance=0.3,
            ),
        }

        query_result = ArticlesQueryResult(
            articles=articles,
            metadata=metadata,
            next_cursor=None,
            has_more=False,
        )

        with patch.object(ArticleRepository, "build_articles_base_query"):
            with patch.object(
                ArticleRepository,
                "execute_articles_query",
                new=AsyncMock(return_value=query_result),
            ):
                with patch.object(
                    ArticleRepository,
                    "get_article_tags",
                    new=AsyncMock(return_value={}),
                ):
                    result = await app._search_articles_with_score(
                        "test", user_id, 10
                    )

            # Scores should be normalized to 0-1 range
            scores = [hit["score"] for hit in result]
            assert max(scores) <= 1.0
            assert min(scores) >= 0.0

    @pytest.mark.asyncio
    async def test_search_feeds_with_score_normalizes_scores(self):
        """Should normalize feed scores."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        user_id = uuid4()
        feed_id = uuid4()

        mock_result = {
            "data": [
                {
                    "id": feed_id,
                    "title": "Test Feed",
                    "website": "https://example.com",
                    "is_active": True,
                    "is_pinned": False,
                    "unread_count": 5,
                    "_relevance": 1.2,
                }
            ],
            "pagination": {
                "total": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False,
            },
        }

        app.repository.search_feeds = AsyncMock(return_value=mock_result)

        result = await app._search_feeds_with_score("test", user_id, 10)

        assert len(result) == 1
        # Score should be normalized (1.2 / 1.5 = 0.8, clamped to 0-1)
        assert result[0]["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_search_tags_with_score_normalizes_scores(self):
        """Should normalize tag scores."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        user_id = uuid4()
        tag_id = uuid4()

        mock_result = {
            "data": [
                {
                    "id": tag_id,
                    "name": "test-tag",
                    "article_count": 10,
                    "_relevance": 1.3,
                }
            ],
            "pagination": {
                "total": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False,
            },
        }

        app.repository.search_tags = AsyncMock(return_value=mock_result)

        result = await app._search_tags_with_score("test", user_id, 10)

        assert len(result) == 1
        # Score should be normalized (1.3 / 1.5 ≈ 0.87)
        assert result[0]["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_search_folders_with_score_normalizes_scores(self):
        """Should normalize folder scores."""
        mock_db = AsyncMock()
        app = SearchApplication(mock_db)

        user_id = uuid4()
        folder_id = uuid4()

        mock_result = {
            "data": [
                {
                    "id": folder_id,
                    "name": "Tech",
                    "unread_count": 15,
                    "is_pinned": True,
                    "_relevance": 1.1,
                }
            ],
            "pagination": {
                "total": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False,
            },
        }

        app.repository.search_folders = AsyncMock(return_value=mock_result)

        result = await app._search_folders_with_score("tech", user_id, 10)

        assert len(result) == 1
        # Score should be normalized (1.1 / 1.5 ≈ 0.73)
        assert result[0]["score"] <= 1.0


class TestNormalizeScores:
    """Test _normalize_scores helper method."""

    def test_normalize_scores_with_range(self):
        """Should apply min-max normalization when range > 0."""
        app = SearchApplication(AsyncMock())

        hits = [
            {"_relevance": 0.5, "id": uuid4(), "title": "A"},
            {"_relevance": 0.8, "id": uuid4(), "title": "B"},
            {"_relevance": 0.6, "id": uuid4(), "title": "C"},
        ]

        result = app._normalize_scores(hits)

        scores = [hit["score"] for hit in result]
        # Min should be 0, max should be 1
        assert min(scores) == 0.0
        assert max(scores) == 1.0

    def test_normalize_scores_single_result(self):
        """Should clamp score to 0-1 for single result."""
        app = SearchApplication(AsyncMock())

        hits = [{"_relevance": 2.5, "id": uuid4(), "title": "A"}]

        result = app._normalize_scores(hits)

        # Single high score should be clamped to 1.0
        assert result[0]["score"] == 1.0

    def test_normalize_scores_all_same_relevance(self):
        """Should clamp scores when all relevances are equal."""
        app = SearchApplication(AsyncMock())

        hits = [
            {"_relevance": 0.5, "id": uuid4(), "title": "A"},
            {"_relevance": 0.5, "id": uuid4(), "title": "B"},
        ]

        result = app._normalize_scores(hits)

        # All should be clamped to 0-1
        scores = [hit["score"] for hit in result]
        assert all(0.0 <= s <= 1.0 for s in scores)

    def test_normalize_scores_empty_list(self):
        """Should return empty list for empty input."""
        app = SearchApplication(AsyncMock())

        result = app._normalize_scores([])

        assert result == []


class TestDictToUnifiedHit:
    """Test _dict_to_unified_hit helper method."""

    def test_dict_to_unified_hit_article(self):
        """Should convert article dict to ArticleListResponse."""
        app = SearchApplication(AsyncMock())

        article_id = uuid4()
        hit_dict = {
            "type": "articles",
            "score": 0.8,
            "id": article_id,
            "title": "Test Article",
            "data": {
                "id": article_id,
                "title": "Test Article",
                "summary": "Test summary",
                "published_at": None,
                "is_read": False,
                "read_later": False,
                "media_url": None,
                "feeds": [],
            },
        }

        result = app._dict_to_unified_hit(hit_dict, "article")

        assert result.type == "article"
        assert isinstance(result.data, ArticleListResponse)
        assert result.data.title == "Test Article"

    def test_dict_to_unified_hit_feed(self):
        """Should convert feed dict to FeedSearchHit."""
        app = SearchApplication(AsyncMock())

        feed_id = uuid4()
        hit_dict = {
            "type": "feeds",
            "score": 0.9,
            "id": feed_id,
            "title": "Test Feed",
            "data": {
                "id": feed_id,
                "title": "Test Feed",
                "website": "https://example.com",
                "is_active": True,
                "is_pinned": False,
                "unread_count": 5,
            },
        }

        result = app._dict_to_unified_hit(hit_dict, "feed")

        assert result.type == "feed"
        assert result.data.title == "Test Feed"

    def test_dict_to_unified_hit_tag(self):
        """Should convert tag dict to TagSearchHit."""
        app = SearchApplication(AsyncMock())

        tag_id = uuid4()
        hit_dict = {
            "type": "tags",
            "score": 0.7,
            "id": tag_id,
            "title": "test-tag",
            "data": {
                "id": tag_id,
                "name": "test-tag",
                "article_count": 10,
            },
        }

        result = app._dict_to_unified_hit(hit_dict, "tag")

        assert result.type == "tag"
        assert result.data.name == "test-tag"

    def test_dict_to_unified_hit_folder(self):
        """Should convert folder dict to FolderSearchHit."""
        app = SearchApplication(AsyncMock())

        folder_id = uuid4()
        hit_dict = {
            "type": "folders",
            "score": 0.6,
            "id": folder_id,
            "title": "Tech",
            "data": {
                "id": folder_id,
                "name": "Tech",
                "unread_count": 15,
                "is_pinned": True,
            },
        }

        result = app._dict_to_unified_hit(hit_dict, "folder")

        assert result.type == "folder"
        assert result.data.name == "Tech"

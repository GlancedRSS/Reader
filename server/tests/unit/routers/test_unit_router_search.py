"""Unit tests for search endpoints."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.models import User
from backend.routers.search import (
    search_feeds,
    search_folders,
    search_tags,
    universal_search,
)


class TestUniversalSearch:
    """Test universal search endpoint."""

    @pytest.mark.asyncio
    async def test_calls_search_app_with_request_and_user(self):
        """Should call search_app.universal_search with request and user."""
        query = "test query"
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_response = MagicMock()
        mock_search_app.universal_search = AsyncMock(return_value=mock_response)

        response = await universal_search(
            q=query, search_app=mock_search_app, current_user=user
        )

        mock_search_app.universal_search.assert_called_once()
        call_args = mock_search_app.universal_search.call_args
        assert call_args[0][1] == user
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_creates_unified_search_request_with_query(self):
        """Should create UnifiedSearchRequest with query."""
        query = "python programming"
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_search_app.universal_search = AsyncMock(return_value=MagicMock())

        await universal_search(
            q=query, search_app=mock_search_app, current_user=user
        )

        call_args = mock_search_app.universal_search.call_args
        request = call_args[0][0]
        assert request.query == query


class TestSearchFeeds:
    """Test feeds search endpoint."""

    @pytest.mark.asyncio
    async def test_calls_search_app_with_feed_request(self):
        """Should call search_app.search_feeds with correct request."""
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_response = MagicMock()
        mock_search_app.search_feeds = AsyncMock(return_value=mock_response)

        response = await search_feeds(
            q="tech",
            limit=10,
            offset=5,
            search_app=mock_search_app,
            current_user=user,
        )

        mock_search_app.search_feeds.assert_called_once()
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_creates_request_with_query_limit_offset(self):
        """Should create FeedSearchRequest with query, limit, and offset."""
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_search_app.search_feeds = AsyncMock(return_value=MagicMock())

        await search_feeds(
            q="news",
            limit=25,
            offset=10,
            search_app=mock_search_app,
            current_user=user,
        )

        call_args = mock_search_app.search_feeds.call_args
        request = call_args[0][0]
        assert request.query == "news"
        assert request.limit == 25
        assert request.offset == 10


class TestSearchTags:
    """Test tags search endpoint."""

    @pytest.mark.asyncio
    async def test_calls_search_app_with_tag_request(self):
        """Should call search_app.search_tags with correct request."""
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_response = MagicMock()
        mock_search_app.search_tags = AsyncMock(return_value=mock_response)

        response = await search_tags(
            q="python",
            limit=15,
            offset=2,
            search_app=mock_search_app,
            current_user=user,
        )

        mock_search_app.search_tags.assert_called_once()
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_creates_request_with_all_params(self):
        """Should create TagSearchRequest with query, limit, and offset."""
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_search_app.search_tags = AsyncMock(return_value=MagicMock())

        await search_tags(
            q="coding",
            limit=30,
            offset=5,
            search_app=mock_search_app,
            current_user=user,
        )

        call_args = mock_search_app.search_tags.call_args
        request = call_args[0][0]
        assert request.query == "coding"
        assert request.limit == 30
        assert request.offset == 5


class TestSearchFolders:
    """Test folders search endpoint."""

    @pytest.mark.asyncio
    async def test_calls_search_app_with_folder_request(self):
        """Should call search_app.search_folders with correct request."""
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_response = MagicMock()
        mock_search_app.search_folders = AsyncMock(return_value=mock_response)

        response = await search_folders(
            q="work",
            limit=12,
            offset=3,
            search_app=mock_search_app,
            current_user=user,
        )

        mock_search_app.search_folders.assert_called_once()
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_creates_request_with_all_params(self):
        """Should create FolderSearchRequest with query, limit, and offset."""
        user = User(id=uuid4(), username="testuser")
        mock_search_app = MagicMock()
        mock_search_app.search_folders = AsyncMock(return_value=MagicMock())

        await search_folders(
            q="projects",
            limit=40,
            offset=8,
            search_app=mock_search_app,
            current_user=user,
        )

        call_args = mock_search_app.search_folders.call_args
        request = call_args[0][0]
        assert request.query == "projects"
        assert request.limit == 40
        assert request.offset == 8

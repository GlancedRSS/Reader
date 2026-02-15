"""Unit tests for SearchRepository."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.infrastructure.repositories.search import SearchRepository


class TestSearchFeeds:
    """Test search_feeds method."""

    @pytest.mark.asyncio
    async def test_search_feeds_basic(self):
        """Should execute feed search with query."""
        mock_db = AsyncMock()
        repo = SearchRepository(mock_db)

        user_id = uuid4()

        mock_rows = MagicMock()
        mock_rows.all.return_value = []
        mock_db.execute.return_value = mock_rows
        mock_db.execute.return_value = mock_rows

        result = await repo.search_feeds(query="test", user_id=user_id)

        assert "data" in result
        assert "pagination" in result

    @pytest.mark.asyncio
    async def test_search_feeds_with_offset_and_limit(self):
        """Should apply offset-based pagination."""
        mock_db = AsyncMock()
        repo = SearchRepository(mock_db)

        user_id = uuid4()

        mock_rows = MagicMock()
        mock_rows.all.return_value = []
        mock_count = MagicMock()
        mock_count.scalar.return_value = 0

        # Execute is called multiple times, return appropriate values
        execute_results = [mock_count, mock_rows]
        mock_db.execute.side_effect = execute_results

        result = await repo.search_feeds(
            query="test", user_id=user_id, offset=10, limit=5
        )

        assert result["pagination"]["offset"] == 10
        assert result["pagination"]["limit"] == 5


class TestSearchTags:
    """Test search_tags method."""

    @pytest.mark.asyncio
    async def test_search_tags_basic(self):
        """Should execute tag search with query."""
        mock_db = AsyncMock()
        repo = SearchRepository(mock_db)

        user_id = uuid4()

        mock_rows = MagicMock()
        mock_rows.all.return_value = []
        mock_count = MagicMock()
        mock_count.scalar.return_value = 0

        execute_results = [mock_count, mock_rows]
        mock_db.execute.side_effect = execute_results

        result = await repo.search_tags(query="test", user_id=user_id)

        assert "data" in result
        assert "pagination" in result

    @pytest.mark.asyncio
    async def test_search_tags_with_limit(self):
        """Should respect limit parameter."""
        mock_db = AsyncMock()
        repo = SearchRepository(mock_db)

        user_id = uuid4()

        mock_rows = MagicMock()
        mock_rows.all.return_value = []
        mock_count = MagicMock()
        mock_count.scalar.return_value = 0

        execute_results = [mock_count, mock_rows]
        mock_db.execute.side_effect = execute_results

        result = await repo.search_tags(query="test", user_id=user_id, limit=10)

        assert result["pagination"]["limit"] == 10


class TestSearchFolders:
    """Test search_folders method."""

    @pytest.mark.asyncio
    async def test_search_folders_basic(self):
        """Should execute folder search with query."""
        mock_db = AsyncMock()
        repo = SearchRepository(mock_db)

        user_id = uuid4()

        mock_rows = MagicMock()
        mock_rows.all.return_value = []
        mock_count = MagicMock()
        mock_count.scalar.return_value = 0

        execute_results = [mock_count, mock_rows]
        mock_db.execute.side_effect = execute_results

        result = await repo.search_folders(query="test", user_id=user_id)

        assert "data" in result
        assert "pagination" in result

    @pytest.mark.asyncio
    async def test_search_folders_with_limit(self):
        """Should respect limit parameter."""
        mock_db = AsyncMock()
        repo = SearchRepository(mock_db)

        user_id = uuid4()

        mock_rows = MagicMock()
        mock_rows.all.return_value = []
        mock_count = MagicMock()
        mock_count.scalar.return_value = 0

        execute_results = [mock_count, mock_rows]
        mock_db.execute.side_effect = execute_results

        result = await repo.search_folders(
            query="test", user_id=user_id, limit=25
        )

        assert result["pagination"]["limit"] == 25

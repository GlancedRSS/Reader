"""Unit tests for database functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core import database


class TestInitDb:
    """Test database initialization."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables_successfully(self):
        """Should initialize database and create tables."""
        mock_conn = AsyncMock()
        # First call: SELECT 1, Second call: table count query
        result1 = MagicMock()
        result1.scalar = MagicMock(return_value=1)
        result2 = MagicMock()
        result2.scalar = MagicMock(return_value=42)
        mock_conn.execute = AsyncMock(side_effect=[result1, result2])
        mock_conn.run_sync = MagicMock()

        mock_begin_context = AsyncMock()
        mock_begin_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin_context.__aexit__ = AsyncMock()

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=mock_begin_context)

        with patch("backend.core.database.engine", mock_engine):
            await database.init_db()

        # Verify run_sync was called (create_all goes through run_sync)
        mock_conn.run_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_db_logs_and_raises_exception_on_failure(self):
        """Should log exception and re-raise when database initialization fails."""
        from contextlib import asynccontextmanager

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(
            side_effect=Exception("Connection failed")
        )

        @asynccontextmanager
        async def mock_begin():
            yield mock_conn

        mock_engine = MagicMock()
        mock_engine.begin = mock_begin

        with patch("backend.core.database.engine", mock_engine):
            with pytest.raises(Exception, match="Connection failed"):
                await database.init_db()


class TestCheckDatabaseHealth:
    """Test database health check."""

    @pytest.mark.asyncio
    async def test_check_database_health_returns_healthy_when_tables_exist(
        self,
    ):
        """Should return healthy status when database is accessible and has tables."""
        mock_conn = AsyncMock()
        # SELECT 1 returns 1, table count returns 10
        result1 = MagicMock()
        result1.scalar = MagicMock(return_value=1)
        result2 = MagicMock()
        result2.scalar = MagicMock(return_value=10)
        mock_conn.execute = AsyncMock(side_effect=[result1, result2])

        mock_begin_context = AsyncMock()
        mock_begin_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin_context.__aexit__ = AsyncMock()

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=mock_begin_context)

        with patch("backend.core.database.engine", mock_engine):
            is_healthy, message = await database.check_database_health()

        assert is_healthy is True
        assert "Database healthy" in message
        assert "10 tables" in message

    @pytest.mark.asyncio
    async def test_check_database_health_returns_unhealthy_when_no_tables(self):
        """Should return unhealthy status when no tables found."""
        mock_conn = AsyncMock()
        # SELECT 1 returns 1, table count returns 0
        result1 = MagicMock()
        result1.scalar = MagicMock(return_value=1)
        result2 = MagicMock()
        result2.scalar = MagicMock(return_value=0)
        mock_conn.execute = AsyncMock(side_effect=[result1, result2])

        mock_begin_context = AsyncMock()
        mock_begin_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin_context.__aexit__ = AsyncMock()

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=mock_begin_context)

        with patch("backend.core.database.engine", mock_engine):
            is_healthy, message = await database.check_database_health()

        assert is_healthy is False
        assert message == "No tables found in database"

    @pytest.mark.asyncio
    async def test_check_database_health_returns_unhealthy_on_query_failure(
        self,
    ):
        """Should return unhealthy status when SELECT 1 fails."""
        mock_conn = AsyncMock()
        result = MagicMock()
        result.scalar = MagicMock(return_value=None)  # Not 1
        mock_conn.execute = AsyncMock(return_value=result)

        mock_begin_context = AsyncMock()
        mock_begin_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin_context.__aexit__ = AsyncMock()

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=mock_begin_context)

        with patch("backend.core.database.engine", mock_engine):
            is_healthy, message = await database.check_database_health()

        assert is_healthy is False
        assert message == "Database query failed"

    @pytest.mark.asyncio
    async def test_check_database_health_returns_unhealthy_on_exception(self):
        """Should return unhealthy status when connection fails."""
        from contextlib import asynccontextmanager

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(side_effect=Exception("Connection lost"))

        @asynccontextmanager
        async def mock_begin():
            yield mock_conn

        mock_engine = MagicMock()
        mock_engine.begin = mock_begin

        with patch("backend.core.database.engine", mock_engine):
            is_healthy, message = await database.check_database_health()

        assert is_healthy is False
        assert "Database connection failed" in message
        assert "Connection lost" in message

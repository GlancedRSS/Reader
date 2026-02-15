"""Unit tests for Arq worker functions.

These tests focus on configuration and logging.
Full integration testing of worker handlers is done at the handler level.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.workers import functions


class TestStartup:
    """Test worker startup function."""

    @pytest.mark.asyncio
    async def test_startup_logs(self):
        """Should log startup message."""
        with patch("backend.workers.functions.logger") as mock_logger:
            await functions.startup({})

            mock_logger.info.assert_called_once_with("Arq worker starting up")


class TestShutdown:
    """Test worker shutdown function."""

    @pytest.mark.asyncio
    async def test_shutdown_logs(self):
        """Should log shutdown and close connections."""
        with patch("backend.workers.functions.logger") as mock_logger:
            mock_engine = MagicMock()
            mock_engine.dispose = AsyncMock()
            with patch("backend.core.database.engine", new=mock_engine):
                with patch(
                    "backend.infrastructure.external.redis.close_redis",
                    new=AsyncMock(),
                ):
                    await functions.shutdown({})

                    # Verify shutdown was logged
                    assert mock_logger.info.call_count >= 3
                    calls = [
                        call.args[0] for call in mock_logger.info.call_args_list
                    ]
                    assert "initiating graceful shutdown" in calls[0].lower()
                    assert "shutdown completed" in calls[-1].lower()


class TestOpmlImport:
    """Test OPML import worker function."""

    @pytest.mark.asyncio
    async def test_opml_import_logs_info(self):
        """Should log import info."""
        with patch("backend.workers.functions.logger") as mock_logger:
            mock_handler = MagicMock()
            mock_response = MagicMock()
            mock_response.model_dump.return_value = {"status": "success"}
            mock_handler.handle = AsyncMock(return_value=mock_response)

            with patch(
                "backend.infrastructure.jobs.opml.OpmlImportJobHandler",
                return_value=mock_handler,
            ):
                await functions.opml_import(
                    ctx={},
                    user_id="00000000-0000-0000-0000-000000000001",
                    import_id="00000000-0000-0000-0000-000000000002",
                    storage_key="uploads/test.opml",
                    filename="test.opml",
                )

                # Should log the import
                assert mock_logger.info.called


class TestOpmlExport:
    """Test OPML export worker function."""

    @pytest.mark.asyncio
    async def test_opml_export_logs_info(self):
        """Should log export info."""
        with patch("backend.workers.functions.logger") as mock_logger:
            mock_handler = MagicMock()
            mock_response = MagicMock()
            mock_response.model_dump.return_value = {"status": "success"}
            mock_handler.handle = AsyncMock(return_value=mock_response)

            with patch(
                "backend.infrastructure.jobs.opml.OpmlExportJobHandler",
                return_value=mock_handler,
            ):
                await functions.opml_export(
                    ctx={},
                    user_id="00000000-0000-0000-0000-000000000001",
                    export_id="00000000-0000-0000-0000-000000000002",
                )

                assert mock_logger.info.called

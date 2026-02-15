"""Unit tests for application lifecycle management."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core import lifecycle


class TestGracefulShutdown:
    """Test graceful shutdown functionality."""

    def setup_method(self):
        """Reset global state before each test."""
        lifecycle.shutdown_event.clear()
        lifecycle.active_requests.clear()
        lifecycle.background_tasks.clear()
        lifecycle.logger = None

    @pytest.mark.asyncio
    async def test_initializes_logger_when_none(self):
        """Should initialize structlog when logger is None."""
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    await lifecycle.graceful_shutdown()

        mock_get_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_sets_shutdown_event(self):
        """Should set the shutdown event."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    await lifecycle.graceful_shutdown()

        assert lifecycle.shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_cancels_background_tasks(self):
        """Should cancel all background tasks."""
        mock_task = MagicMock(spec=asyncio.Task)
        mock_task.cancel = MagicMock()

        lifecycle.background_tasks.add(mock_task)

        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    with patch("asyncio.gather", new=AsyncMock()):
                        await lifecycle.graceful_shutdown()

        mock_task.cancel.assert_called_once()
        assert len(lifecycle.background_tasks) == 0

    @pytest.mark.asyncio
    async def test_gathers_background_tasks_with_return_exceptions(self):
        """Should gather background tasks with return_exceptions=True."""
        task1 = AsyncMock()
        task2 = AsyncMock()
        lifecycle.background_tasks = {task1, task2}

        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    with patch("asyncio.gather") as mock_gather:
                        mock_gather.return_value = AsyncMock()
                        await lifecycle.graceful_shutdown()

                        call_kwargs = mock_gather.call_args[1]
                        assert call_kwargs.get("return_exceptions") is True

    @pytest.mark.asyncio
    async def test_waits_for_active_requests_with_timeout(self):
        """Should wait for active requests with 10 second timeout."""
        request_task = MagicMock(spec=asyncio.Task)
        lifecycle.active_requests.add(request_task)

        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    with patch("asyncio.wait_for") as mock_wait:
                        mock_wait.return_value = AsyncMock()
                        await lifecycle.graceful_shutdown()

                        call_args = mock_wait.call_args
                        assert call_args[1].get("timeout") == 10.0

    @pytest.mark.asyncio
    async def test_gathers_active_requests_with_return_exceptions(self):
        """Should gather active requests with return_exceptions=True."""
        request_task = MagicMock(spec=asyncio.Task)
        lifecycle.active_requests.add(request_task)

        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    with patch("asyncio.wait_for"):
                        with patch("asyncio.gather") as mock_gather:
                            await lifecycle.graceful_shutdown()

                        # Verify gather was called (could be 1 or 2 times depending on background_tasks)
                        assert mock_gather.call_count >= 1
                        # Check that return_exceptions=True was used in at least one call
                        found_return_exceptions = False
                        for call in mock_gather.call_args_list:
                            if call[1].get("return_exceptions") is True:
                                found_return_exceptions = True
                                break
                        assert found_return_exceptions, (
                            "No call to gather had return_exceptions=True"
                        )

    @pytest.mark.asyncio
    async def test_logs_warning_on_timeout(self):
        """Should log warning when requests timeout."""
        request_task = MagicMock(spec=asyncio.Task)
        lifecycle.active_requests.add(request_task)

        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    with patch("asyncio.wait_for", side_effect=TimeoutError()):
                        await lifecycle.graceful_shutdown()

        mock_logger.warning.assert_called()
        args = mock_logger.warning.call_args[0]
        assert "did not complete in time" in args[0]

    @pytest.mark.asyncio
    async def test_closes_redis_connection(self):
        """Should close Redis connection."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ) as mock_close:
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    await lifecycle.graceful_shutdown()

        mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_logs_redis_close_error(self):
        """Should log error when closing Redis fails."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(side_effect=Exception("Redis error")),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    await lifecycle.graceful_shutdown()

        mock_logger.exception.assert_called()
        args = mock_logger.exception.call_args[0]
        assert "Redis connection" in args[0]

    @pytest.mark.asyncio
    async def test_closes_database_connections(self):
        """Should close database connections."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    await lifecycle.graceful_shutdown()

        mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_logs_database_close_error(self):
        """Should log error when closing database fails."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock(
                        side_effect=Exception("DB error")
                    )
                    await lifecycle.graceful_shutdown()

        mock_logger.exception.assert_called()
        args = mock_logger.exception.call_args[0]
        assert "database connections" in args[0]

    @pytest.mark.asyncio
    async def test_handles_empty_background_tasks(self):
        """Should handle empty background tasks set."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    await lifecycle.graceful_shutdown()

        # Should not raise any exception

    @pytest.mark.asyncio
    async def test_handles_empty_active_requests(self):
        """Should handle empty active requests set."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.infrastructure.external.redis.close_redis",
                new=AsyncMock(),
            ):
                with patch("backend.core.database.engine") as mock_engine:
                    mock_engine.dispose = AsyncMock()
                    await lifecycle.graceful_shutdown()

        # Should not raise any exception


class TestLifespanInit:
    """Test lifespan initialization."""

    def setup_method(self):
        """Reset global state before each test."""
        lifecycle.shutdown_event.clear()
        lifecycle.active_requests.clear()
        lifecycle.background_tasks.clear()
        lifecycle.logger = None

    @pytest.mark.asyncio
    async def test_initializes_logger(self):
        """Should initialize structlog on startup."""
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                await lifecycle.lifespan_init()

        mock_get_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_logs_startup_info(self):
        """Should log startup information."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                with patch(
                                    "backend.core.app.settings"
                                ) as mock_settings:
                                    mock_settings.environment = "test"
                                    await lifecycle.lifespan_init()

        mock_logger.info.assert_called()
        # Check that "Starting" was logged
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Starting" in call for call in info_calls)

    @pytest.mark.asyncio
    async def test_validates_configuration(self):
        """Should validate configuration on startup."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration"
            ) as mock_validate:
                mock_validate.return_value = (True, [])

                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                await lifecycle.lifespan_init()

        mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_on_config_validation_failure(self):
        """Should raise exception when config validation fails."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration"
            ) as mock_validate:
                mock_validate.return_value = (False, ["Invalid DATABASE_URL"])

                with patch(
                    "backend.core.app.get_configuration_help"
                ) as mock_help:
                    mock_help.return_value = {
                        "DATABASE_URL": "Set a valid PostgreSQL URL"
                    }

                    with pytest.raises(
                        Exception, match="Configuration validation failed"
                    ):
                        await lifecycle.lifespan_init()

    @pytest.mark.asyncio
    async def test_logs_config_validation_errors(self):
        """Should log configuration errors."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.core.app.validate_configuration"
            ) as mock_validate:
                mock_validate.return_value = (False, ["error1", "error2"])

                with patch("backend.core.app.get_configuration_help"):
                    with pytest.raises(
                        Exception, match="Configuration validation failed"
                    ):
                        await lifecycle.lifespan_init()

        # Check that errors were logged
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any(
            "Configuration validation failed" in call for call in error_calls
        )

    @pytest.mark.asyncio
    async def test_logs_configuration_help_on_failure(self):
        """Should log configuration help when validation fails."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.core.app.validate_configuration"
            ) as mock_validate:
                mock_validate.return_value = (
                    False,
                    ["DATABASE_URL is required"],
                )

                with patch(
                    "backend.core.app.get_configuration_help"
                ) as mock_help:
                    mock_help.return_value = {
                        "DATABASE_URL": "PostgreSQL connection string"
                    }

                    with pytest.raises(
                        Exception, match="Configuration validation failed"
                    ):
                        await lifecycle.lifespan_init()

        # Should log configuration help
        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_initializes_database(self):
        """Should initialize database connection."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db") as mock_init:
                    mock_init.return_value = AsyncMock()

                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                await lifecycle.lifespan_init()

        mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_on_database_init_failure(self):
        """Should raise exception when database init fails."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db") as mock_init:
                    mock_init.side_effect = Exception("DB connection failed")

                    with pytest.raises(
                        Exception, match="Database initialization failed"
                    ):
                        await lifecycle.lifespan_init()

    @pytest.mark.asyncio
    async def test_initializes_redis_connection(self):
        """Should initialize Redis connection."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                await lifecycle.lifespan_init()

        mock_redis.assert_called_once()
        mock_redis.return_value.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_enables_keyspace_notifications(self):
        """Should enable Redis keyspace notifications."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                await lifecycle.lifespan_init()

        mock_redis.return_value.config_set.assert_called_once_with(
            "notify-keyspace-events", "Ex"
        )

    @pytest.mark.asyncio
    async def test_logs_warning_on_keyspace_config_failure(self):
        """Should log warning when keyspace config fails."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock(
                            side_effect=Exception("Config failed")
                        )

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                await lifecycle.lifespan_init()

        mock_logger.warning.assert_called()
        args = mock_logger.warning.call_args[0]
        assert "keyspace notifications" in args[0]

    @pytest.mark.asyncio
    async def test_starts_background_task_for_notifications(self):
        """Should start background task for listening to timer expirations."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            mock_task = MagicMock()
                            mock_task.add_done_callback = MagicMock()

                            with patch(
                                "asyncio.create_task", return_value=mock_task
                            ) as mock_create:
                                await lifecycle.lifespan_init()

        mock_create.assert_called_once()
        mock_task.add_done_callback.assert_called_once()
        assert len(lifecycle.background_tasks) == 1

    @pytest.mark.asyncio
    async def test_continues_without_redis_in_development(self):
        """Should continue without Redis in non-production environment."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.side_effect = Exception("Redis unavailable")

                        with patch(
                            "backend.core.app.settings"
                        ) as mock_settings:
                            mock_settings.environment = "development"

                            # Should not raise
                            await lifecycle.lifespan_init()

        # Should log a warning about Redis
        mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_raises_on_redis_failure_in_production(self):
        """Should raise exception when Redis fails in production."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.side_effect = Exception("Redis unavailable")

                        with patch(
                            "backend.core.app.settings"
                        ) as mock_settings:
                            mock_settings.environment = "production"

                            with pytest.raises(
                                Exception, match="Redis initialization failed"
                            ):
                                await lifecycle.lifespan_init()

    @pytest.mark.asyncio
    async def test_logs_background_job_system_info(self):
        """Should log about background job system."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.core.app.validate_configuration",
                return_value=(True, []),
            ):
                with patch("backend.core.database.init_db", new=AsyncMock()):
                    with patch(
                        "backend.infrastructure.external.redis.get_redis_client"
                    ) as mock_redis:
                        mock_redis.return_value = AsyncMock()
                        mock_redis.return_value.ping = AsyncMock()
                        mock_redis.return_value.config_set = AsyncMock()

                        with patch(
                            "backend.infrastructure.notifications.notifications.listen_for_timer_expirations_with_restart"
                        ):
                            with patch("asyncio.create_task"):
                                await lifecycle.lifespan_init()

        # Check that "Background job system" was logged
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Background job system" in call for call in info_calls)


class TestLifespanShutdown:
    """Test lifespan shutdown callback."""

    def setup_method(self):
        """Reset global state before each test."""
        lifecycle.shutdown_event.clear()
        lifecycle.active_requests.clear()
        lifecycle.background_tasks.clear()
        lifecycle.logger = None

    @pytest.mark.asyncio
    async def test_initializes_logger_when_none(self):
        """Should initialize logger if None before shutdown."""
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            with patch(
                "backend.core.lifecycle.graceful_shutdown", new=AsyncMock()
            ):
                await lifecycle.lifespan_shutdown()

        mock_get_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_existing_logger(self):
        """Should use existing logger if already initialized."""
        existing_logger = MagicMock()
        lifecycle.logger = existing_logger

        with patch("structlog.get_logger") as mock_get_logger:
            with patch(
                "backend.core.lifecycle.graceful_shutdown", new=AsyncMock()
            ):
                await lifecycle.lifespan_shutdown()

        # Should not call get_logger if logger already exists
        mock_get_logger.assert_not_called()

    @pytest.mark.asyncio
    async def test_calls_graceful_shutdown(self):
        """Should call graceful_shutdown."""
        with patch("structlog.get_logger"):
            with patch(
                "backend.core.lifecycle.graceful_shutdown", new=AsyncMock()
            ) as mock_shutdown:
                await lifecycle.lifespan_shutdown()

        mock_shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_logs_shutdown_info(self):
        """Should log shutdown initiation."""
        mock_logger = MagicMock()

        with patch("structlog.get_logger", return_value=mock_logger):
            with patch(
                "backend.core.lifecycle.graceful_shutdown", new=AsyncMock()
            ):
                await lifecycle.lifespan_shutdown()

        mock_logger.info.assert_called()
        args = mock_logger.info.call_args[0]
        assert "lifespan" in args[0].lower() or "shutdown" in args[0].lower()

"""Unit tests for Arq worker settings."""

from unittest.mock import patch

import pytest

from backend.workers.settings import WorkerSettings, get_redis_settings


class TestGetRedisSettings:
    """Test Redis settings configuration."""

    @pytest.mark.asyncio
    async def test_returns_redis_settings_with_default(self):
        """Should return RedisSettings with default localhost."""
        with patch("backend.workers.settings.settings") as mock_settings:
            mock_settings.redis_url = None

            result = get_redis_settings()

            assert result.host == "localhost"
            assert result.port == 6379
            assert result.database == 0

    @pytest.mark.asyncio
    async def test_parses_custom_redis_url(self):
        """Should parse custom Redis URL."""
        with (
            patch("backend.workers.settings.settings") as mock_settings,
            patch("backend.workers.settings._parse_redis_url") as mock_parse,
        ):
            mock_settings.redis_url = "redis://custom-redis:6380"
            mock_parse.return_value = ("custom-redis", 6380)

            result = get_redis_settings()

            assert result.host == "custom-redis"
            assert result.port == 6380
            mock_parse.assert_called_once_with("redis://custom-redis:6380")


class TestWorkerSettings:
    """Test WorkerSettings configuration."""

    @pytest.mark.asyncio
    async def test_has_redis_settings(self):
        """Should have Redis settings configured."""
        assert WorkerSettings.redis_settings is not None
        assert isinstance(WorkerSettings.redis_settings, object)

    @pytest.mark.asyncio
    async def test_has_worker_functions(self):
        """Should have worker functions registered."""
        assert len(WorkerSettings.functions) == 3

        function_names = [f.name for f in WorkerSettings.functions]
        assert "opml_import" in function_names
        assert "opml_export" in function_names
        assert "feed_create_and_subscribe" in function_names

    @pytest.mark.asyncio
    async def test_has_cron_jobs(self):
        """Should have cron jobs configured."""
        assert len(WorkerSettings.cron_jobs) == 3

        cron_names = [job.name for job in WorkerSettings.cron_jobs]
        assert "scheduled_feed_refresh" in cron_names
        assert "scheduled_feed_cleanup" in cron_names
        assert "scheduled_auto_mark_read" in cron_names

    @pytest.mark.asyncio
    async def test_feed_refresh_cron_schedule(self):
        """Feed refresh should run every 15 minutes."""
        job = next(
            j
            for j in WorkerSettings.cron_jobs
            if j.name == "scheduled_feed_refresh"
        )

        assert job.minute == set(range(0, 60, 15))
        assert job.hour is None
        assert job.second == 0

    @pytest.mark.asyncio
    async def test_feed_cleanup_cron_schedule(self):
        """Feed cleanup should run daily at 2 AM."""
        job = next(
            j
            for j in WorkerSettings.cron_jobs
            if j.name == "scheduled_feed_cleanup"
        )

        assert job.hour == 2
        assert job.minute == 0
        assert job.second == 0

    @pytest.mark.asyncio
    async def test_auto_mark_read_cron_schedule(self):
        """Auto-mark read should run daily at 3 AM."""
        job = next(
            j
            for j in WorkerSettings.cron_jobs
            if j.name == "scheduled_auto_mark_read"
        )

        assert job.hour == 3
        assert job.minute == 0
        assert job.second == 0

    @pytest.mark.asyncio
    async def test_has_startup_shutdown_hooks(self):
        """Should have startup and shutdown functions."""
        assert WorkerSettings.on_startup is not None
        assert WorkerSettings.on_shutdown is not None

    @pytest.mark.asyncio
    async def test_job_timeout_is_one_hour(self):
        """Job timeout should be 1 hour for OPML imports."""
        assert WorkerSettings.job_timeout == 3600

    @pytest.mark.asyncio
    async def test_max_concurrent_jobs(self):
        """Should allow 10 concurrent jobs."""
        assert WorkerSettings.max_jobs == 10

    @pytest.mark.asyncio
    async def test_max_tries(self):
        """Should retry failed jobs 3 times."""
        assert WorkerSettings.max_tries == 3

    @pytest.mark.asyncio
    async def test_result_expiration(self):
        """Job results should expire after 1 hour."""
        assert WorkerSettings.result_expires == 3600

    @pytest.mark.asyncio
    async def test_poll_delay(self):
        """Should poll every 0.5 seconds."""
        assert WorkerSettings.poll_delay == 0.5

    @pytest.mark.asyncio
    async def test_queue_name(self):
        """Should use arq:queue as queue name."""
        assert WorkerSettings.queue_name == "arq:queue"

    @pytest.mark.asyncio
    async def test_allow_select_jobs(self):
        """Should allow selective job execution."""
        assert WorkerSettings.allow_select_jobs is True

    @pytest.mark.asyncio
    async def test_use_uvloop(self):
        """Should use uvloop for performance."""
        assert WorkerSettings.use_uvloop is True

    @pytest.mark.asyncio
    async def test_cron_jobs_do_not_run_at_startup(self):
        """Cron jobs should not run immediately at startup."""
        for job in WorkerSettings.cron_jobs:
            assert job.run_at_startup is False

    @pytest.mark.asyncio
    async def test_cron_jobs_are_not_unique(self):
        """Cron jobs should allow overlapping runs."""
        for job in WorkerSettings.cron_jobs:
            assert job.unique is False

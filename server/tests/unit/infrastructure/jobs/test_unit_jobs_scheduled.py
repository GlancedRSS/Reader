"""Unit tests for scheduled maintenance job handlers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.infrastructure.jobs.scheduled import (
    FeedCleanupHandler,
    ScheduledFeedRefreshCycleHandler,
)
from backend.schemas.workers import (
    FeedCleanupJobRequest,
    ScheduledFeedRefreshCycleJobRequest,
)


class TestFeedCleanupHandler:
    """Test feed cleanup job handler."""

    @pytest.mark.asyncio
    async def test_marks_orphaned_feeds_inactive(self):
        """Should mark feeds with no subscribers as inactive."""
        handler = FeedCleanupHandler()

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_feed_repo = MagicMock()
            mock_feed_repo.bulk_mark_orphaned_feeds_inactive = AsyncMock(
                return_value=5
            )

            with patch(
                "backend.infrastructure.jobs.scheduled.FeedRepository",
                return_value=mock_feed_repo,
            ):
                request = FeedCleanupJobRequest(job_id=str(uuid.uuid4()))

                result = await handler.execute(request)

                assert result.status == "success"
                assert result.inactive_feeds == 5
                assert "Marked 5 feeds" in result.message

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_orphaned_feeds(self):
        """Should return zero when no feeds need cleanup."""
        handler = FeedCleanupHandler()

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_feed_repo = MagicMock()
            mock_feed_repo.bulk_mark_orphaned_feeds_inactive = AsyncMock(
                return_value=0
            )

            with patch(
                "backend.infrastructure.jobs.scheduled.FeedRepository",
                return_value=mock_feed_repo,
            ):
                request = FeedCleanupJobRequest(job_id=str(uuid.uuid4()))

                result = await handler.execute(request)

                assert result.inactive_feeds == 0


class TestScheduledFeedRefreshCycleHandler:
    """Test scheduled feed refresh cycle handler."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_active_feeds(self):
        """Should return early when there are no active feeds."""
        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            # Simulate empty result
            mock_result = MagicMock()
            mock_result.all.return_value = []

            mock_db.execute = AsyncMock(return_value=mock_result)

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            assert result.feeds_total == 0
            assert result.feeds_processed == 0
            assert result.message == "No feeds to refresh"

    @pytest.mark.asyncio
    async def test_processes_feeds_in_batches(self):
        """Should process feeds in configured batch sizes."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4() for _ in range(10)]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            # Simulate query returning 10 feeds
            mock_result = MagicMock()
            mock_result.all.return_value = [(fid,) for fid in feed_ids]
            mock_db.execute = AsyncMock(return_value=mock_result)

            with patch("backend.core.app.settings") as mock_settings:
                mock_settings.feed_refresh_batch_size = 3

                # Mock _process_feed_with_session to return success
                handler._process_feed_with_session = AsyncMock(
                    return_value={"status": "success", "new_articles": 2}
                )

                request = ScheduledFeedRefreshCycleJobRequest(
                    job_id=str(uuid.uuid4())
                )

                result = await handler.execute(request)

                # Should process in 4 batches (3 + 3 + 3 + 1)
                assert handler._process_feed_with_session.call_count == 10
                assert result.feeds_total == 10
                assert result.feeds_successful == 10
                assert result.new_articles_total == 20

    @pytest.mark.asyncio
    async def test_counts_failed_feeds(self):
        """Should count failed feeds correctly."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4() for _ in range(5)]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_result = MagicMock()
            mock_result.all.return_value = [(fid,) for fid in feed_ids]
            mock_db.execute = AsyncMock(return_value=mock_result)

            # Mock some successes and some failures
            call_count = 0

            async def mock_process(feed_id):
                nonlocal call_count
                call_count += 1
                if call_count in [2, 4]:  # 2nd and 4th feed fails
                    return {"status": "error", "message": "Feed error"}
                return {"status": "success", "new_articles": 1}

            handler._process_feed_with_session = mock_process

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            assert result.feeds_total == 5
            assert result.feeds_successful == 3
            assert result.feeds_failed == 2

    @pytest.mark.asyncio
    async def test_handles_exceptions_in_batch(self):
        """Should handle exceptions when processing feeds."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4() for _ in range(3)]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_result = MagicMock()
            mock_result.all.return_value = [(fid,) for fid in feed_ids]
            mock_db.execute = AsyncMock(return_value=mock_result)

            # Mock some exceptions
            call_count = 0

            async def mock_process(feed_id):
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise Exception("Network error")
                return {"status": "success", "new_articles": 1}

            handler._process_feed_with_session = mock_process

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            assert result.feeds_total == 3
            assert result.feeds_successful == 2
            assert result.feeds_failed == 1

    @pytest.mark.asyncio
    async def test_tracks_duration(self):
        """Should track processing duration."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4()]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_result = MagicMock()
            mock_result.all.return_value = [(feed_ids[0],)]
            mock_db.execute = AsyncMock(return_value=mock_result)

            handler._process_feed_with_session = AsyncMock(
                return_value={"status": "success", "new_articles": 0}
            )

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_counts_skipped_feeds_as_successful(self):
        """Should count skipped feeds as processed but not failed."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4() for _ in range(3)]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_result = MagicMock()
            mock_result.all.return_value = [(fid,) for fid in feed_ids]
            mock_db.execute = AsyncMock(return_value=mock_result)

            handler._process_feed_with_session = AsyncMock(
                side_effect=[
                    {"status": "success", "new_articles": 1},
                    {"status": "skipped"},
                    {"status": "error"},
                ]
            )

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            # Skipped counts as successful
            assert result.feeds_successful == 2
            assert result.feeds_failed == 1

    @pytest.mark.asyncio
    async def test_handles_unknown_status(self):
        """Should handle unknown result status."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4()]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_result = MagicMock()
            mock_result.all.return_value = [(feed_ids[0],)]
            mock_db.execute = AsyncMock(return_value=mock_result)

            handler._process_feed_with_session = AsyncMock(
                return_value={"status": "unknown_status"}
            )

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            # Unknown status counts as failed
            assert result.feeds_failed == 1

    @pytest.mark.asyncio
    async def test_handles_unexpected_result_type(self):
        """Should handle unexpected result types."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4()]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_result = MagicMock()
            mock_result.all.return_value = [(feed_ids[0],)]
            mock_db.execute = AsyncMock(return_value=mock_result)

            handler._process_feed_with_session = AsyncMock(
                return_value="invalid"
            )

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            # Unexpected type counts as failed
            assert result.feeds_failed == 1

    @pytest.mark.asyncio
    async def test_tallies_new_articles(self):
        """Should correctly tally new articles across all feeds."""
        from uuid import uuid4

        mock_feed_app = MagicMock()
        handler = ScheduledFeedRefreshCycleHandler(mock_feed_app)

        feed_ids = [uuid4() for _ in range(3)]

        with patch(
            "backend.infrastructure.jobs.scheduled.AsyncSessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            mock_result = MagicMock()
            mock_result.all.return_value = [(fid,) for fid in feed_ids]
            mock_db.execute = AsyncMock(return_value=mock_result)

            handler._process_feed_with_session = AsyncMock(
                side_effect=[
                    {"status": "success", "new_articles": 5},
                    {"status": "success", "new_articles": 10},
                    {"status": "success", "new_articles": 3},
                ]
            )

            request = ScheduledFeedRefreshCycleJobRequest(
                job_id=str(uuid.uuid4())
            )

            result = await handler.execute(request)

            assert result.new_articles_total == 18

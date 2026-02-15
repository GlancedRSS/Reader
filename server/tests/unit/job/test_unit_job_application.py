"""Unit tests for JobApplication."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.application.job import JobApplication


class TestJobApplicationGetJob:
    """Test job retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_job_returns_job_data_when_exists(self):
        """Should return job data when job exists in Redis."""
        mock_cache_instance = AsyncMock()
        mock_cache_instance.get = AsyncMock(
            return_value={"job_id": "test123", "status": "pending"}
        )

        with patch(
            "backend.application.job.job.get_cache",
            return_value=mock_cache_instance,
        ):
            app = JobApplication()
            result = await app.get_job("test123")

        assert result == {"job_id": "test123", "status": "pending"}
        mock_cache_instance.get.assert_called_once_with("job:test123")

    @pytest.mark.asyncio
    async def test_get_job_returns_none_when_not_exists(self):
        """Should return None when job doesn't exist in Redis."""
        mock_cache_instance = AsyncMock()
        mock_cache_instance.get = AsyncMock(return_value=None)

        with patch(
            "backend.application.job.job.get_cache",
            return_value=mock_cache_instance,
        ):
            app = JobApplication()
            result = await app.get_job("nonexistent")

        assert result is None
        mock_cache_instance.get.assert_called_once_with("job:nonexistent")


class TestJobApplicationUpdateJob:
    """Test job update operations."""

    @pytest.mark.asyncio
    async def test_update_job_updates_existing_job(self):
        """Should update job status when job exists."""
        mock_cache_instance = AsyncMock()
        mock_cache_instance.get = AsyncMock(
            return_value={"job_id": "test123", "status": "pending"}
        )
        mock_cache_instance.set = AsyncMock()

        with patch(
            "backend.application.job.job.get_cache",
            return_value=mock_cache_instance,
        ):
            app = JobApplication()
            await app.update_job("test123", "completed", result={"count": 5})

        # Verify set was called with updated job data
        mock_cache_instance.set.assert_called_once()
        call_args = mock_cache_instance.set.call_args
        assert call_args[0][0] == "job:test123"
        updated_job = call_args[0][1]
        assert updated_job["status"] == "completed"
        assert updated_job["result"] == {"count": 5}
        assert updated_job["error"] is None
        assert "completed_at" in updated_job
        assert call_args[1]["expire"] == 3600

    @pytest.mark.asyncio
    async def test_update_job_with_error(self):
        """Should update job with error message."""
        mock_cache_instance = AsyncMock()
        mock_cache_instance.get = AsyncMock(
            return_value={"job_id": "test123", "status": "pending"}
        )
        mock_cache_instance.set = AsyncMock()

        with patch(
            "backend.application.job.job.get_cache",
            return_value=mock_cache_instance,
        ):
            app = JobApplication()
            await app.update_job(
                "test123", "failed", error="Something went wrong"
            )

        call_args = mock_cache_instance.set.call_args
        updated_job = call_args[0][1]
        assert updated_job["status"] == "failed"
        assert updated_job["error"] == "Something went wrong"
        assert updated_job["result"] is None

    @pytest.mark.asyncio
    async def test_update_job_with_result_and_error(self):
        """Should update job with both result and error."""
        mock_cache_instance = AsyncMock()
        mock_cache_instance.get = AsyncMock(
            return_value={"job_id": "test123", "status": "pending"}
        )
        mock_cache_instance.set = AsyncMock()

        with patch(
            "backend.application.job.job.get_cache",
            return_value=mock_cache_instance,
        ):
            app = JobApplication()
            await app.update_job(
                "test123",
                "completed",
                result={"processed": 10},
                error="Partial failure",
            )

        call_args = mock_cache_instance.set.call_args
        updated_job = call_args[0][1]
        assert updated_job["result"] == {"processed": 10}
        assert updated_job["error"] == "Partial failure"

    @pytest.mark.asyncio
    async def test_update_job_returns_silently_when_job_not_exists(self):
        """Should return without error when job doesn't exist."""
        mock_cache_instance = AsyncMock()
        mock_cache_instance.get = AsyncMock(return_value=None)
        mock_cache_instance.set = AsyncMock()

        with patch(
            "backend.application.job.job.get_cache",
            return_value=mock_cache_instance,
        ):
            app = JobApplication()
            # Should not raise an exception
            await app.update_job("nonexistent", "completed")

        # set should not be called when job doesn't exist
        mock_cache_instance.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_job_sets_completed_at_timestamp(self):
        """Should set completed_at timestamp when updating job."""
        from datetime import UTC, datetime

        mock_cache_instance = AsyncMock()
        mock_cache_instance.get = AsyncMock(
            return_value={"job_id": "test123", "status": "running"}
        )
        mock_cache_instance.set = AsyncMock()

        with patch(
            "backend.application.job.job.get_cache",
            return_value=mock_cache_instance,
        ):
            app = JobApplication()
            before_update = datetime.now(UTC)
            await app.update_job("test123", "completed")
            after_update = datetime.now(UTC)

        call_args = mock_cache_instance.set.call_args
        updated_job = call_args[0][1]
        completed_at = updated_job["completed_at"]

        # Verify timestamp is set and is within expected range
        assert completed_at >= before_update
        assert completed_at <= after_update

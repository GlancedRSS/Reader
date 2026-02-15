"""Unit tests for auto-mark read job handler."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.infrastructure.jobs.auto_read import AutoMarkReadJobHandler
from backend.schemas.workers import AutoMarkReadJobRequest


class TestAutoMarkReadJobHandlerBulkMode:
    """Test bulk mode (all users) for auto-mark read job."""

    @pytest.mark.asyncio
    async def test_bulk_mode_calls_repository(self):
        """Should call bulk_mark_old_articles_as_read in bulk mode."""
        mock_user_repo = MagicMock()
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.bulk_mark_old_articles_as_read = AsyncMock(
            return_value={"users_affected": 5, "articles_marked": 100}
        )

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()),
            user_id=None,  # Bulk mode
        )

        result = await handler.execute(request)

        assert result.status == "success"
        assert result.users_processed == 5
        assert result.articles_marked_read == 100
        mock_subscription_repo.bulk_mark_old_articles_as_read.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_mode_calculates_cutoff_dates(self):
        """Should calculate correct cutoff dates for bulk mode."""

        mock_user_repo = MagicMock()
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.bulk_mark_old_articles_as_read = AsyncMock(
            return_value={"users_affected": 1, "articles_marked": 10}
        )

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(job_id=str(uuid4()), user_id=None)

        await handler.execute(request)

        call_args = (
            mock_subscription_repo.bulk_mark_old_articles_as_read.call_args
        )
        now = datetime.now(UTC)

        # Verify cutoff dates are approximately correct
        cutoff_7 = call_args.kwargs["cutoff_date_7days"]
        cutoff_14 = call_args.kwargs["cutoff_date_14days"]
        cutoff_30 = call_args.kwargs["cutoff_date_30days"]

        assert (now - cutoff_7).days >= 6
        assert (now - cutoff_7).days <= 7
        assert (now - cutoff_14).days >= 13
        assert (now - cutoff_14).days <= 14
        assert (now - cutoff_30).days >= 29
        assert (now - cutoff_30).days <= 30

    @pytest.mark.asyncio
    async def test_bulk_mode_returns_correct_response(self):
        """Should return correct response structure for bulk mode."""
        mock_user_repo = MagicMock()
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.bulk_mark_old_articles_as_read = AsyncMock(
            return_value={"users_affected": 10, "articles_marked": 500}
        )

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(job_id=str(uuid4()), user_id=None)

        result = await handler.execute(request)

        assert result.users_skipped == 0
        assert "Processed 10 users" in result.message
        assert "marked 500 articles" in result.message


class TestAutoMarkReadJobHandlerSingleUserMode:
    """Test single-user mode for auto-mark read job."""

    @pytest.mark.asyncio
    async def test_single_user_mode_returns_not_found(self):
        """Should return not found response when user doesn't exist."""
        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=None)
        mock_subscription_repo = MagicMock()

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(uuid4())
        )

        result = await handler.execute(request)

        assert result.status == "success"
        assert result.users_processed == 0
        assert result.articles_marked_read == 0
        assert result.message == "User not found"

    @pytest.mark.asyncio
    async def test_single_user_mode_skips_when_disabled(self):
        """Should skip when auto-mark as read is disabled for user."""
        user_id = uuid4()
        mock_user = MagicMock()
        mock_user.id = user_id

        mock_prefs = MagicMock()
        mock_prefs.auto_mark_as_read = "disabled"

        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_user_repo.get_user_preferences = AsyncMock(return_value=mock_prefs)
        mock_subscription_repo = MagicMock()

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(user_id)
        )

        result = await handler.execute(request)

        assert result.users_processed == 0
        assert result.articles_marked_read == 0
        assert result.users_skipped == 1
        assert "disabled" in result.message.lower()

    @pytest.mark.asyncio
    async def test_single_user_mode_skips_when_no_preferences(self):
        """Should skip when user preferences are not set."""
        user_id = uuid4()
        mock_user = MagicMock()
        mock_user.id = user_id

        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_user_repo.get_user_preferences = AsyncMock(return_value=None)
        mock_subscription_repo = MagicMock()

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(user_id)
        )

        result = await handler.execute(request)

        assert result.users_processed == 0
        assert result.articles_marked_read == 0
        assert result.users_skipped == 1

    @pytest.mark.asyncio
    async def test_single_user_mode_skips_when_no_unread_articles(self):
        """Should skip when there are no unread articles to mark."""
        user_id = uuid4()
        mock_user = MagicMock()
        mock_user.id = user_id

        mock_prefs = MagicMock()
        mock_prefs.auto_mark_as_read = "7_days"

        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_user_repo.get_user_preferences = AsyncMock(return_value=mock_prefs)
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.get_unread_articles_for_user = AsyncMock(
            return_value=[]
        )

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(user_id)
        )

        result = await handler.execute(request)

        assert result.users_processed == 0
        assert result.users_skipped == 1
        assert "No unread articles" in result.message

    @pytest.mark.asyncio
    async def test_single_user_mode_marks_articles_as_read(self):
        """Should mark articles as read in single-user mode."""
        user_id = uuid4()
        article_id = uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id

        mock_prefs = MagicMock()
        mock_prefs.auto_mark_as_read = "14_days"

        mock_unread = MagicMock()
        mock_unread.article_id = article_id

        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_user_repo.get_user_preferences = AsyncMock(return_value=mock_prefs)
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.get_unread_articles_for_user = AsyncMock(
            return_value=[mock_unread]
        )
        mock_subscription_repo.mark_articles_as_read = AsyncMock(return_value=1)

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(user_id)
        )

        result = await handler.execute(request)

        assert result.users_processed == 1
        assert result.articles_marked_read == 1
        assert result.users_skipped == 0
        mock_subscription_repo.mark_articles_as_read.assert_called_once()

    @pytest.mark.asyncio
    async def test_single_user_mode_uses_correct_cutoff_date(self):
        """Should use correct cutoff date based on user preference."""

        user_id = uuid4()
        mock_user = MagicMock()
        mock_user.id = user_id

        mock_prefs = MagicMock()
        mock_prefs.auto_mark_as_read = "30_days"

        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_user_repo.get_user_preferences = AsyncMock(return_value=mock_prefs)
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.get_unread_articles_for_user = AsyncMock(
            return_value=[]
        )

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(user_id)
        )

        await handler.execute(request)

        call_args = (
            mock_subscription_repo.get_unread_articles_for_user.call_args
        )
        cutoff_date = call_args.args[1]  # Second argument is cutoff_date
        now = datetime.now(UTC)

        # Should be approximately 30 days ago
        assert (now - cutoff_date).days >= 29
        assert (now - cutoff_date).days <= 30

    @pytest.mark.asyncio
    async def test_single_user_mode_handles_multiple_articles(self):
        """Should handle multiple unread articles correctly."""
        user_id = uuid4()
        article_id_1 = uuid4()
        article_id_2 = uuid4()
        article_id_3 = uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id

        mock_prefs = MagicMock()
        mock_prefs.auto_mark_as_read = "7_days"

        mock_unread_list = [
            MagicMock(article_id=article_id_1),
            MagicMock(article_id=article_id_2),
            MagicMock(article_id=article_id_3),
        ]

        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_user_repo.get_user_preferences = AsyncMock(return_value=mock_prefs)
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.get_unread_articles_for_user = AsyncMock(
            return_value=mock_unread_list
        )
        mock_subscription_repo.mark_articles_as_read = AsyncMock(return_value=3)

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(user_id)
        )

        result = await handler.execute(request)

        assert result.articles_marked_read == 3
        mock_subscription_repo.mark_articles_as_read.assert_called_once_with(
            user_id, [article_id_1, article_id_2, article_id_3]
        )

    @pytest.mark.asyncio
    async def test_single_user_mode_defaults_to_7_days(self):
        """Should default to 7 days for invalid preference value."""
        user_id = uuid4()
        mock_user = MagicMock()
        mock_user.id = user_id

        mock_prefs = MagicMock()
        mock_prefs.auto_mark_as_read = "invalid_value"

        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_user_repo.get_user_preferences = AsyncMock(return_value=mock_prefs)
        mock_subscription_repo = MagicMock()
        mock_subscription_repo.get_unread_articles_for_user = AsyncMock(
            return_value=[]
        )

        handler = AutoMarkReadJobHandler(mock_user_repo, mock_subscription_repo)
        request = AutoMarkReadJobRequest(
            job_id=str(uuid4()), user_id=str(user_id)
        )

        await handler.execute(request)

        call_args = (
            mock_subscription_repo.get_unread_articles_for_user.call_args
        )
        cutoff_date = call_args.args[1]
        now = datetime.now(UTC)

        # Should default to 7 days
        assert (now - cutoff_date).days >= 6
        assert (now - cutoff_date).days <= 7

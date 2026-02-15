"""Unit tests for OpmlApplication."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.opml import OpmlApplication
from backend.schemas.domain import (
    OpmlExportRequest,
    OpmlImport,
)


class TestOpmlApplicationValidateFolderOwnership:
    """Test folder ownership validation."""

    @pytest.mark.asyncio
    async def test_validate_folder_ownership_returns_true_when_owned(
        self, db_session: AsyncSession
    ):
        """Should return True when folder exists and user owns it."""
        folder_id = "123e4567-e89b-12d3-a456-426614174000"
        user_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_folder = MagicMock()
        mock_folder_repo = MagicMock()
        mock_folder_repo.get_folder_by_id_and_user = AsyncMock(
            return_value=mock_folder
        )

        app = OpmlApplication(db_session)
        app.folder_repo = mock_folder_repo

        result = await app.validate_folder_ownership(folder_id, user_id)

        assert result is True
        mock_folder_repo.get_folder_by_id_and_user.assert_called_once_with(
            folder_id, user_id
        )

    @pytest.mark.asyncio
    async def test_validate_folder_ownership_returns_false_when_not_owned(
        self, db_session: AsyncSession
    ):
        """Should return False when folder doesn't exist or user doesn't own it."""
        folder_id = "123e4567-e89b-12d3-a456-426614174000"
        user_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_folder_repo = MagicMock()
        mock_folder_repo.get_folder_by_id_and_user = AsyncMock(
            return_value=None
        )

        app = OpmlApplication(db_session)
        app.folder_repo = mock_folder_repo

        result = await app.validate_folder_ownership(folder_id, user_id)

        assert result is False


class TestOpmlApplicationExportOpml:
    """Test OPML export operations."""

    @pytest.mark.asyncio
    async def test_export_opml_enqueues_job_successfully(
        self, db_session: AsyncSession
    ):
        """Should enqueue export job successfully with ArqClient."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        request = OpmlExportRequest(folder_id=None)

        mock_arq_client = MagicMock()
        mock_arq_client.enqueue_job = AsyncMock()

        with patch(
            "backend.application.opml.opml.ArqClient",
            return_value=mock_arq_client,
        ):
            app = OpmlApplication(db_session)
            response = await app.export_opml(request, user_id)

        assert "queued successfully" in response.message.lower()
        mock_arq_client.enqueue_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_opml_includes_folder_id_when_provided(
        self, db_session: AsyncSession
    ):
        """Should include folder_id in job enqueue when provided."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        folder_id = "123e4567-e89b-12d3-a456-426614174002"
        request = OpmlExportRequest(folder_id=folder_id)

        mock_arq_client = MagicMock()
        mock_arq_client.enqueue_job = AsyncMock()

        with patch(
            "backend.application.opml.opml.ArqClient",
            return_value=mock_arq_client,
        ):
            app = OpmlApplication(db_session)
            await app.export_opml(request, user_id)

        call_kwargs = mock_arq_client.enqueue_job.call_args.kwargs
        assert call_kwargs["folder_id"] == str(folder_id)

    @pytest.mark.asyncio
    async def test_export_opml_raises_500_when_enqueue_fails(
        self, db_session: AsyncSession
    ):
        """Should raise 500 INTERNAL_SERVER_ERROR when enqueue fails."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        request = OpmlExportRequest(folder_id=None)

        mock_arq_client = MagicMock()
        mock_arq_client.enqueue_job = AsyncMock(
            side_effect=Exception("Redis connection failed")
        )

        with patch(
            "backend.application.opml.opml.ArqClient",
            return_value=mock_arq_client,
        ):
            app = OpmlApplication(db_session)

            with pytest.raises(HTTPException) as exc_info:
                await app.export_opml(request, user_id)

        assert exc_info.value.status_code == 500
        assert "Failed to queue export job" in exc_info.value.detail


class TestOpmlApplicationImportOpml:
    """Test OPML import operations."""

    @pytest.mark.asyncio
    async def test_import_opml_enqueues_job_successfully(
        self, db_session: AsyncSession
    ):
        """Should enqueue import job successfully when file exists."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        import_id = "123e4567-e89b-12d3-a456-426614174002"
        request = OpmlImport(import_id=import_id, folder_id=None)

        mock_opml_import = MagicMock()
        mock_opml_import.user_id = user_id
        mock_opml_import.id = import_id
        mock_opml_import.storage_key = "users/test/imports/test.opml"
        mock_opml_import.filename = "test.opml"

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=mock_opml_import)

        mock_storage_client = MagicMock()
        mock_storage_client.file_exists = MagicMock(return_value=True)

        mock_arq_client = MagicMock()
        mock_arq_client.enqueue_job = AsyncMock()

        with patch(
            "backend.application.opml.opml.ArqClient",
            return_value=mock_arq_client,
        ):
            app = OpmlApplication(db_session)
            app.repository = mock_repo
            app._get_storage_client = MagicMock(
                return_value=mock_storage_client
            )

            response = await app.import_opml(request, user_id)

        assert "queued successfully" in response.message.lower()
        mock_arq_client.enqueue_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_opml_raises_404_when_import_not_found(
        self, db_session: AsyncSession
    ):
        """Should raise 404 NOT_FOUND when import record doesn't exist."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        import_id = "123e4567-e89b-12d3-a456-426614174002"
        request = OpmlImport(import_id=import_id, folder_id=None)

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=None)

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(HTTPException) as exc_info:
            await app.import_opml(request, user_id)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_import_opml_raises_404_when_user_mismatch(
        self, db_session: AsyncSession
    ):
        """Should raise 404 NOT_FOUND when import belongs to different user."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        other_user_id = "123e4567-e89b-12d3-a456-426614174003"
        import_id = "123e4567-e89b-12d3-a456-426614174002"
        request = OpmlImport(import_id=import_id, folder_id=None)

        mock_opml_import = MagicMock()
        mock_opml_import.user_id = other_user_id

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=mock_opml_import)

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(HTTPException) as exc_info:
            await app.import_opml(request, user_id)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_import_opml_raises_400_when_no_storage_key(
        self, db_session: AsyncSession
    ):
        """Should raise 400 BAD_REQUEST when storage_key is None."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        import_id = "123e4567-e89b-12d3-a456-426614174002"
        request = OpmlImport(import_id=import_id, folder_id=None)

        mock_opml_import = MagicMock()
        mock_opml_import.user_id = user_id
        mock_opml_import.storage_key = None

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=mock_opml_import)

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(HTTPException) as exc_info:
            await app.import_opml(request, user_id)

        assert exc_info.value.status_code == 400
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_import_opml_raises_400_when_file_expired(
        self, db_session: AsyncSession
    ):
        """Should raise 400 BAD_REQUEST when file doesn't exist in storage."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        import_id = "123e4567-e89b-12d3-a456-426614174002"
        request = OpmlImport(import_id=import_id, folder_id=None)

        mock_opml_import = MagicMock()
        mock_opml_import.user_id = user_id
        mock_opml_import.storage_key = "users/test/imports/test.opml"
        mock_opml_import.filename = "test.opml"

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=mock_opml_import)

        mock_storage_client = MagicMock()
        mock_storage_client.file_exists = MagicMock(return_value=False)

        app = OpmlApplication(db_session)
        app.repository = mock_repo
        app._get_storage_client = MagicMock(return_value=mock_storage_client)

        with pytest.raises(HTTPException) as exc_info:
            await app.import_opml(request, user_id)

        assert exc_info.value.status_code == 400
        assert "expired" in exc_info.value.detail.lower()


class TestOpmlApplicationGetOpmlStatusById:
    """Test get OPML status operations."""

    @pytest.mark.asyncio
    async def test_get_opml_status_returns_operation_info(
        self, db_session: AsyncSession
    ):
        """Should return operation info when record exists."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        job_id = UUID("123e4567-e89b-12d3-a456-426614174002")

        mock_record = MagicMock()
        mock_record.id = job_id
        mock_record.status = "completed"
        mock_record.filename = "test.opml"
        mock_record.created_at = "2024-01-01T00:00:00Z"
        mock_record.completed_at = "2024-01-01T00:05:00Z"
        mock_record.total_feeds = 10
        mock_record.imported_feeds = 8
        mock_record.failed_feeds = 1
        mock_record.duplicate_feeds = 1
        mock_record.failed_feeds_log = None

        mock_repo = MagicMock()
        mock_repo.get_opml_by_id = AsyncMock(return_value=mock_record)

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        response = await app.get_opml_status_by_id(job_id, user_id)

        assert response.id == job_id
        assert response.status == "completed"
        assert response.total_feeds == 10

    @pytest.mark.asyncio
    async def test_get_opml_status_raises_404_when_not_found(
        self, db_session: AsyncSession
    ):
        """Should raise 404 NOT_FOUND when record doesn't exist."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        job_id = UUID("123e4567-e89b-12d3-a456-426614174002")

        mock_repo = MagicMock()
        mock_repo.get_opml_by_id = AsyncMock(return_value=None)

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(HTTPException) as exc_info:
            await app.get_opml_status_by_id(job_id, user_id)

        assert exc_info.value.status_code == 404


class TestOpmlApplicationRollbackImport:
    """Test OPML import rollback operations."""

    @pytest.mark.asyncio
    async def test_rollback_import_deletes_subscriptions(
        self, db_session: AsyncSession
    ):
        """Should delete subscriptions and return count."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        import_id = "123e4567-e89b-12d3-a456-426614174002"

        mock_opml_import = MagicMock()
        mock_opml_import.user_id = user_id

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=mock_opml_import)

        mock_execute_result = MagicMock()
        mock_execute_result.all = MagicMock(return_value=[])
        mock_execute_result.rowcount = 5
        db_session.execute = AsyncMock(return_value=mock_execute_result)
        db_session.commit = AsyncMock()

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        result = await app.rollback_import(import_id, user_id)

        assert result == 5
        db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_rollback_import_raises_404_when_not_found(
        self, db_session: AsyncSession
    ):
        """Should raise 404 NOT_FOUND when import doesn't exist."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        import_id = "123e4567-e89b-12d3-a456-426614174002"

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=None)

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(HTTPException) as exc_info:
            await app.rollback_import(import_id, user_id)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_rollback_import_raises_404_when_user_mismatch(
        self, db_session: AsyncSession
    ):
        """Should raise 404 NOT_FOUND when import belongs to different user."""
        user_id = "123e4567-e89b-12d3-a456-426614174001"
        other_user_id = "123e4567-e89b-12d3-a456-426614174003"
        import_id = "123e4567-e89b-12d3-a456-426614174002"

        mock_opml_import = MagicMock()
        mock_opml_import.user_id = other_user_id

        mock_repo = MagicMock()
        mock_repo.get_import_by_id = AsyncMock(return_value=mock_opml_import)

        app = OpmlApplication(db_session)
        app.repository = mock_repo

        with pytest.raises(HTTPException) as exc_info:
            await app.rollback_import(import_id, user_id)

        assert exc_info.value.status_code == 404

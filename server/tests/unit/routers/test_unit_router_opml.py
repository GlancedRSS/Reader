"""Unit tests for OPML endpoints."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import UploadFile
from fastapi.responses import FileResponse

from backend.models import User
from backend.routers.opml import (
    download_opml_by_filename,
    export_opml,
    get_opml_status,
    rollback_opml_import,
    upload_opml,
)
from backend.schemas.core import ResponseMessage
from backend.schemas.domain import OpmlExportRequest, OpmlOperationResponse


class TestUploadOpml:
    """Test OPML upload endpoint."""

    @pytest.mark.asyncio
    async def test_reads_file_and_calls_upload_and_import(self):
        """Should read file content and call upload and import methods."""
        import_id = uuid4()
        folder_id = uuid4()
        user = User(id=uuid4(), username="testuser")

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.opml"
        mock_file.read = AsyncMock(return_value=b"<opml>content</opml>")

        mock_opml_app = MagicMock()
        mock_upload_response = MagicMock()
        mock_upload_response.import_id = import_id
        mock_opml_app.upload_opml_file = AsyncMock(
            return_value=mock_upload_response
        )
        mock_opml_app.import_opml = AsyncMock(
            return_value=ResponseMessage(message="Import successful")
        )

        response = await upload_opml(mock_file, folder_id, user, mock_opml_app)

        mock_file.read.assert_called_once()
        mock_opml_app.upload_opml_file.assert_called_once()
        mock_opml_app.import_opml.assert_called_once()
        assert response.message == "Import successful"

    @pytest.mark.asyncio
    async def test_uses_default_filename_when_missing(self):
        """Should use default filename when file.filename is None."""
        user = User(id=uuid4(), username="testuser")

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = None
        mock_file.read = AsyncMock(return_value=b"content")

        mock_opml_app = MagicMock()
        mock_upload_response = MagicMock()
        mock_upload_response.import_id = uuid4()
        mock_opml_app.upload_opml_file = AsyncMock(
            return_value=mock_upload_response
        )
        mock_opml_app.import_opml = AsyncMock(return_value=MagicMock())

        await upload_opml(mock_file, None, user, mock_opml_app)

        call_args = mock_opml_app.upload_opml_file.call_args
        assert call_args[1]["filename"] == "upload.opml"

    @pytest.mark.asyncio
    async def test_passes_folder_id_to_import_request(self):
        """Should include folder_id in import request."""
        import_id = uuid4()
        folder_id = uuid4()
        user = User(id=uuid4(), username="testuser")

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "feeds.opml"
        mock_file.read = AsyncMock(return_value=b"content")

        mock_opml_app = MagicMock()
        mock_upload_response = MagicMock()
        mock_upload_response.import_id = import_id
        mock_opml_app.upload_opml_file = AsyncMock(
            return_value=mock_upload_response
        )

        # Capture the import request
        captured_request = None

        def capture_import(request, user_id):
            nonlocal captured_request
            captured_request = request
            return MagicMock()

        mock_opml_app.import_opml = AsyncMock(side_effect=capture_import)

        await upload_opml(mock_file, folder_id, user, mock_opml_app)

        assert captured_request is not None
        assert captured_request.folder_id == folder_id
        assert captured_request.import_id == import_id


class TestExportOpml:
    """Test OPML export endpoint."""

    @pytest.mark.asyncio
    async def test_calls_opml_app_export(self):
        """Should call opml_app.export_opml with request and user_id."""
        request = OpmlExportRequest(feed_ids=[], folder_ids=[])
        user = User(id=uuid4(), username="testuser")

        mock_opml_app = MagicMock()
        mock_response = ResponseMessage(message="Export started")
        mock_opml_app.export_opml = AsyncMock(return_value=mock_response)

        response = await export_opml(request, user, mock_opml_app)

        mock_opml_app.export_opml.assert_called_once_with(request, user.id)
        assert response.message == "Export started"

    @pytest.mark.asyncio
    async def test_passes_user_id_from_current_user(self):
        """Should pass user.id from current_user to export method."""
        request = OpmlExportRequest(feed_ids=[], folder_ids=[])
        user = User(id=uuid4(), username="user")

        mock_opml_app = MagicMock()
        mock_opml_app.export_opml = AsyncMock(return_value=MagicMock())

        await export_opml(request, user, mock_opml_app)

        call_args = mock_opml_app.export_opml.call_args
        assert call_args[0][1] == user.id


class TestGetOpmlStatus:
    """Test get OPML operation status endpoint."""

    @pytest.mark.asyncio
    async def test_calls_opml_app_get_status_by_id(self):
        """Should call opml_app.get_opml_status_by_id with job_id and user_id."""
        job_id = "test-job-123"
        user = User(id=uuid4(), username="testuser")

        mock_opml_app = MagicMock()
        mock_response = MagicMock(spec=OpmlOperationResponse)
        mock_opml_app.get_opml_status_by_id = AsyncMock(
            return_value=mock_response
        )

        response = await get_opml_status(job_id, user, mock_opml_app)

        mock_opml_app.get_opml_status_by_id.assert_called_once_with(
            job_id, user.id
        )
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_returns_opml_operation_response(self):
        """Should return OpmlOperationResponse from application."""
        job_id = "job-456"
        user = User(id=uuid4(), username="user")

        mock_opml_app = MagicMock()
        mock_response = MagicMock(spec=OpmlOperationResponse)
        mock_opml_app.get_opml_status_by_id = AsyncMock(
            return_value=mock_response
        )

        response = await get_opml_status(job_id, user, mock_opml_app)

        assert isinstance(response, MagicMock)


class TestRollbackOpmlImport:
    """Test rollback OPML import endpoint."""

    @pytest.mark.asyncio
    async def test_calls_opml_app_rollback_and_returns_message(self):
        """Should call rollback and return message with deleted count."""
        import_id = uuid4()
        user = User(id=uuid4(), username="testuser")

        mock_opml_app = MagicMock()
        mock_opml_app.rollback_import = AsyncMock(return_value=5)

        response = await rollback_opml_import(import_id, user, mock_opml_app)

        mock_opml_app.rollback_import.assert_called_once_with(
            import_id, user.id
        )
        assert response.message == "Rolled back 5 subscriptions"

    @pytest.mark.asyncio
    async def test_formats_message_with_correct_count(self):
        """Should format message with deleted_count from rollback."""
        import_id = uuid4()
        user = User(id=uuid4(), username="user")

        mock_opml_app = MagicMock()
        mock_opml_app.rollback_import = AsyncMock(return_value=10)

        response = await rollback_opml_import(import_id, user, mock_opml_app)

        assert response.message == "Rolled back 10 subscriptions"
        assert "10" in response.message


class TestDownloadOpmlByFilename:
    """Test download OPML file endpoint."""

    @pytest.mark.asyncio
    async def test_raises_400_for_path_traversal_filename(self):
        """Should raise HTTPException for filename with path separators."""
        user = User(id=uuid4(), username="testuser")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await download_opml_by_filename("../../etc/passwd", user)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_raises_400_for_backslash_in_filename(self):
        """Should raise HTTPException for filename with backslashes."""
        user = User(id=uuid4(), username="testuser")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await download_opml_by_filename("..\\windows\\system32", user)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_raises_404_when_file_not_found(self):
        """Should raise HTTPException when file doesn't exist."""
        user = User(id=uuid4(), username="testuser")

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_client = MagicMock()
            storage_client._base_path = Path(tmpdir)

            with patch(
                "backend.routers.opml.LocalStorageClient",
                return_value=storage_client,
            ):
                from fastapi import HTTPException

                with pytest.raises(HTTPException) as exc_info:
                    await download_opml_by_filename("nonexistent.opml", user)

                assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_file_response_for_valid_file(self):
        """Should return FileResponse for valid, non-expired file."""
        user = User(id=uuid4(), username="testuser")

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create user directory and file
            user_dir = Path(tmpdir) / "users" / str(user.id) / "exports"
            user_dir.mkdir(parents=True)
            test_file = user_dir / "test.opml"
            test_file.write_text("<opml></opml>")

            storage_client = MagicMock()
            storage_client._base_path = Path(tmpdir)

            with patch(
                "backend.routers.opml.LocalStorageClient",
                return_value=storage_client,
            ):
                response = await download_opml_by_filename("test.opml", user)

        assert isinstance(response, FileResponse)
        assert response.media_type == "application/xml"

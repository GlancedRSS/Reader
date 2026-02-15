"""Integration tests for OPML endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestOpmlUploadEndpoint:
    """Test OPML upload endpoint."""

    @pytest.mark.asyncio
    async def test_upload_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Test upload endpoint requires authentication."""
        content = b'<?xml version="1.0"?><opml version="2.0"><head></head><body></body></opml>'
        files = {"file": ("test.opml", content, "application/xml")}

        response = await async_client.post("/api/v1/opml/upload", files=files)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_valid_opml(
        self, authenticated_client: AsyncClient, db_session
    ):
        """Test uploading a valid OPML file."""
        content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <opml version="2.0">
            <head><title>Test Feeds</title></head>
            <body>
                <outline text="Tech Blog" xmlUrl="https://example.com/feed.xml"/>
            </body>
        </opml>"""
        files = {"file": ("test.opml", content, "application/xml")}

        response = await authenticated_client.post(
            "/api/v1/opml/upload", files=files
        )
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        # Note: import_id is not returned because import happens asynchronously
        # The endpoint returns just a success message after queuing the job


class TestOpmlStatusEndpoint:
    """Test OPML status endpoint."""

    @pytest.mark.asyncio
    async def test_status_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Test status endpoint requires authentication."""
        job_id = uuid4()
        response = await async_client.get(f"/api/v1/opml/status/{job_id}")
        assert response.status_code == 401


class TestOpmlRollbackEndpoint:
    """Test OPML rollback endpoint."""

    @pytest.mark.asyncio
    async def test_rollback_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Test rollback endpoint requires authentication."""
        import_id = uuid4()
        response = await async_client.post(f"/api/v1/opml/{import_id}/rollback")
        assert response.status_code == 401


class TestOpmlDownloadEndpoint:
    """Test OPML download endpoint."""

    @pytest.mark.asyncio
    async def test_download_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Test download endpoint requires authentication."""
        filename = "test-file.opml"
        response = await async_client.get(f"/api/v1/opml/download/{filename}")
        assert response.status_code == 401


class TestOpmlExportEndpoint:
    """Test OPML export endpoint."""

    @pytest.mark.asyncio
    async def test_export_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Test export endpoint requires authentication."""
        response = await async_client.post("/api/v1/opml/export")
        assert response.status_code == 401

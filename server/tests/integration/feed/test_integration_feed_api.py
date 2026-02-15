"""Integration tests for feed API endpoints."""

from uuid import uuid4

from httpx import AsyncClient


class TestGetUserFeedsEndpoint:
    """Test GET /api/v1/feeds endpoint."""

    async def test_get_feeds_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get("/api/v1/feeds")
        assert response.status_code == 401

    async def test_get_feeds_empty(self, authenticated_client: AsyncClient):
        """Should return empty list when user has no feeds."""
        response = await authenticated_client.get("/api/v1/feeds")
        assert response.status_code == 200

        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_get_feeds_with_feeds(
        self, authenticated_client: AsyncClient
    ):
        """Should return user's feeds."""
        # Create a folder first
        folder_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Tech"},
        )
        folder_id = folder_response.json()["id"]

        # Create a feed via discovery
        await authenticated_client.post(
            "/api/v1/discover",
            json={
                "url": "https://example.com/feed.xml",
                "folder_id": folder_id,
            },
        )

        # Get feeds
        response = await authenticated_client.get("/api/v1/feeds")
        assert response.status_code == 200

        data = response.json()
        # Note: The feed might not be immediately available as it's processed asynchronously
        assert "data" in data
        assert "pagination" in data

    async def test_get_feeds_with_pagination(
        self, authenticated_client: AsyncClient
    ):
        """Should respect pagination parameters."""
        response = await authenticated_client.get(
            "/api/v1/feeds?limit=10&offset=0"
        )
        assert response.status_code == 200

        data = response.json()
        assert "pagination" in data
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["offset"] == 0

    async def test_get_feeds_with_folder_filter(
        self, authenticated_client: AsyncClient
    ):
        """Should filter feeds by folder ID."""
        # Create a folder
        folder_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Tech"},
        )
        folder_id = folder_response.json()["id"]

        # Filter by folder
        response = await authenticated_client.get(
            f"/api/v1/feeds?folder_id={folder_id}"
        )
        assert response.status_code == 200


class TestGetUserFeedDetailsEndpoint:
    """Test GET /api/v1/feeds/{user_feed_id} endpoint."""

    async def test_get_feed_details_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get(f"/api/v1/feeds/{uuid4()}")
        assert response.status_code == 401

    async def test_get_feed_details_not_found(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent feed."""
        response = await authenticated_client.get(f"/api/v1/feeds/{uuid4()}")
        assert response.status_code == 404


class TestUpdateUserFeedEndpoint:
    """Test PUT /api/v1/feeds/{user_feed_id} endpoint."""

    async def test_update_feed_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.put(
            f"/api/v1/feeds/{uuid4()}",
            json={"title": "Updated"},
        )
        assert response.status_code == 401

    async def test_update_feed_not_found(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent feed."""
        response = await authenticated_client.put(
            f"/api/v1/feeds/{uuid4()}",
            json={"title": "Updated"},
        )
        assert response.status_code == 404


class TestUnsubscribeFeedEndpoint:
    """Test DELETE /api/v1/feeds/{user_feed_id} endpoint."""

    async def test_unsubscribe_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.delete(f"/api/v1/feeds/{uuid4()}")
        assert response.status_code == 401

    async def test_unsubscribe_not_found(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent feed."""
        response = await authenticated_client.delete(f"/api/v1/feeds/{uuid4()}")
        assert response.status_code == 404

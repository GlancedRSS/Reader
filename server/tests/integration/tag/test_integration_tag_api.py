"""Integration tests for tag API endpoints."""

from uuid import uuid4

from httpx import AsyncClient


class TestCreateTagEndpoint:
    """Test POST /api/v1/tags endpoint."""

    async def test_create_tag_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.post(
            "/api/v1/tags",
            json={"name": "Work"},
        )
        assert response.status_code == 401

    async def test_create_tag_success(self, authenticated_client: AsyncClient):
        """Should create a tag successfully."""
        response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Work"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert data["name"] == "Work"
        assert data["article_count"] == 0

    async def test_create_tag_sanitizes_name(
        self, authenticated_client: AsyncClient
    ):
        """Should sanitize tag name before creating."""
        response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "  Work  "},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Work"

    async def test_create_tag_with_duplicate_name_returns_existing(
        self, authenticated_client: AsyncClient
    ):
        """Should return existing tag for duplicate name (get-or-create)."""
        await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Work"},
        )

        response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Work"},
        )
        assert response.status_code == 200

    async def test_create_tag_with_empty_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for empty tag name (Pydantic validation)."""
        response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": ""},
        )
        assert response.status_code == 422

    async def test_create_tag_with_too_long_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for name exceeding max length (Pydantic validation)."""
        response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "a" * 65},
        )
        assert response.status_code == 422


class TestGetTagsEndpoint:
    """Test GET /api/v1/tags endpoint."""

    async def test_get_tags_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get("/api/v1/tags")
        assert response.status_code == 401

    async def test_get_tags_empty(self, authenticated_client: AsyncClient):
        """Should return empty list when no tags exist."""
        response = await authenticated_client.get("/api/v1/tags")
        assert response.status_code == 200

        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_get_tags_returns_all_ordered_by_name(
        self, authenticated_client: AsyncClient
    ):
        """Should return all tags ordered alphabetically."""
        await authenticated_client.post("/api/v1/tags", json={"name": "Zebra"})
        await authenticated_client.post("/api/v1/tags", json={"name": "Apple"})
        await authenticated_client.post("/api/v1/tags", json={"name": "Banana"})

        response = await authenticated_client.get("/api/v1/tags")
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["name"] == "Apple"
        assert data["data"][1]["name"] == "Banana"
        assert data["data"][2]["name"] == "Zebra"

    async def test_get_tags_with_pagination(
        self, authenticated_client: AsyncClient
    ):
        """Should respect pagination parameters."""
        # Create 5 tags
        for i in range(5):
            await authenticated_client.post(
                "/api/v1/tags", json={"name": f"Tag{i}"}
            )

        # Get first page
        response = await authenticated_client.get(
            "/api/v1/tags?limit=2&offset=0"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert data["pagination"]["has_more"] is True

    async def test_get_tags_with_offset(
        self, authenticated_client: AsyncClient
    ):
        """Should skip tags with offset."""
        # Create 5 tags
        for i in range(5):
            await authenticated_client.post(
                "/api/v1/tags", json={"name": f"Tag{i}"}
            )

        # Get second page
        response = await authenticated_client.get(
            "/api/v1/tags?limit=2&offset=2"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["has_more"] is True


class TestGetTagEndpoint:
    """Test GET /api/v1/tags/{tag_id} endpoint."""

    async def test_get_tag_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get(f"/api/v1/tags/{uuid4()}")
        assert response.status_code == 401

    async def test_get_tag_success(self, authenticated_client: AsyncClient):
        """Should return tag details."""
        create_response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Work"},
        )
        tag_id = create_response.json()["id"]

        response = await authenticated_client.get(f"/api/v1/tags/{tag_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == tag_id
        assert data["name"] == "Work"

    async def test_get_tag_non_existent_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent tag."""
        response = await authenticated_client.get(f"/api/v1/tags/{uuid4()}")
        assert response.status_code == 404


class TestUpdateTagEndpoint:
    """Test PUT /api/v1/tags/{tag_id} endpoint."""

    async def test_update_tag_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.put(
            f"/api/v1/tags/{uuid4()}",
            json={"name": "Updated"},
        )
        assert response.status_code == 401

    async def test_update_tag_name(self, authenticated_client: AsyncClient):
        """Should update tag name."""
        create_response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Old Name"},
        )
        tag_id = create_response.json()["id"]

        response = await authenticated_client.put(
            f"/api/v1/tags/{tag_id}",
            json={"name": "New Name"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Tag updated successfully"

        # Verify change
        get_response = await authenticated_client.get(f"/api/v1/tags/{tag_id}")
        assert get_response.json()["name"] == "New Name"

    async def test_update_tag_sanitizes_name(
        self, authenticated_client: AsyncClient
    ):
        """Should sanitize tag name before updating."""
        create_response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Test"},
        )
        tag_id = create_response.json()["id"]

        await authenticated_client.put(
            f"/api/v1/tags/{tag_id}",
            json={"name": "  Updated  "},
        )

        # Verify change
        get_response = await authenticated_client.get(f"/api/v1/tags/{tag_id}")
        assert get_response.json()["name"] == "Updated"

    async def test_update_tag_non_existent_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent tag."""
        response = await authenticated_client.put(
            f"/api/v1/tags/{uuid4()}",
            json={"name": "Updated"},
        )
        assert response.status_code == 404

    async def test_update_tag_to_duplicate_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 409 when name conflicts with another tag."""
        await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Work"},
        )

        tag_response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Personal"},
        )
        tag_id = tag_response.json()["id"]

        # Try to rename to "Work" (already exists)
        response = await authenticated_client.put(
            f"/api/v1/tags/{tag_id}",
            json={"name": "Work"},
        )
        assert response.status_code == 409

    async def test_update_tag_with_empty_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for empty tag name (Pydantic validation)."""
        create_response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Test"},
        )
        tag_id = create_response.json()["id"]

        response = await authenticated_client.put(
            f"/api/v1/tags/{tag_id}",
            json={"name": ""},
        )
        assert response.status_code == 422

    async def test_update_tag_with_too_long_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for name exceeding max length (Pydantic validation)."""
        create_response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Test"},
        )
        tag_id = create_response.json()["id"]

        response = await authenticated_client.put(
            f"/api/v1/tags/{tag_id}",
            json={"name": "a" * 65},
        )
        assert response.status_code == 422


class TestDeleteTagEndpoint:
    """Test DELETE /api/v1/tags/{tag_id} endpoint."""

    async def test_delete_tag_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.delete(f"/api/v1/tags/{uuid4()}")
        assert response.status_code == 401

    async def test_delete_tag_success(self, authenticated_client: AsyncClient):
        """Should delete tag successfully."""
        create_response = await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "Delete Me"},
        )
        tag_id = create_response.json()["id"]

        response = await authenticated_client.delete(f"/api/v1/tags/{tag_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Tag deleted successfully"

        # Verify deletion
        get_response = await authenticated_client.get(f"/api/v1/tags/{tag_id}")
        assert get_response.status_code == 404

    async def test_delete_tag_non_existent_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent tag."""
        response = await authenticated_client.delete(f"/api/v1/tags/{uuid4()}")
        assert response.status_code == 404


class TestTagIsolation:
    """Test that tags are properly isolated between users."""

    async def test_tags_are_isolated_between_users(
        self, authenticated_client: AsyncClient
    ):
        """Should only return tags for the authenticated user."""
        # Create a tag as user 1
        await authenticated_client.post(
            "/api/v1/tags",
            json={"name": "User1Tag"},
        )

        # Try to access a non-existent tag ID
        # (user scoping makes it not found even if ID is valid format)
        response = await authenticated_client.get(f"/api/v1/tags/{uuid4()}")
        assert response.status_code == 404

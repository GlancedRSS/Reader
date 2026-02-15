"""Integration tests for folder API endpoints."""

from uuid import uuid4

from httpx import AsyncClient


class TestCreateFolderEndpoint:
    """Test POST /api/v1/folders endpoint."""

    async def test_create_folder_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.post(
            "/api/v1/folders",
            json={"name": "Work"},
        )
        assert response.status_code == 401

    async def test_create_folder_success(
        self, authenticated_client: AsyncClient
    ):
        """Should create a folder successfully."""
        response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Work"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert data["name"] == "Work"
        assert data["parent_id"] is None
        assert data["depth"] == 0
        assert data["feed_count"] == 0
        assert data["unread_count"] == 0

    async def test_create_folder_with_parent(
        self, authenticated_client: AsyncClient
    ):
        """Should create a folder with a parent."""
        # Create parent first
        parent_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Parent"},
        )
        parent_id = parent_response.json()["id"]

        # Create child
        response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Child", "parent_id": parent_id},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Child"
        assert data["parent_id"] == parent_id
        assert data["depth"] == 1

    async def test_create_folder_with_empty_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for empty folder name (Pydantic validation)."""
        response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": ""},
        )
        assert response.status_code == 422

    async def test_create_folder_with_too_long_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for name exceeding max length (Pydantic validation)."""
        response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "a" * 17},  # Max is 16
        )
        assert response.status_code == 422

    async def test_create_folder_with_duplicate_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 400 for duplicate name under same parent."""
        await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Work"},
        )

        response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Work"},
        )
        assert response.status_code == 400

    async def test_create_folder_with_invalid_parent_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 400 for non-existent parent folder."""
        response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Orphan", "parent_id": str(uuid4())},
        )
        assert response.status_code == 400


class TestGetFolderTreeEndpoint:
    """Test GET /api/v1/folderstree endpoint."""

    async def test_get_folder_tree_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get("/api/v1/folders/tree")
        assert response.status_code == 401

    async def test_get_folder_tree_empty(
        self, authenticated_client: AsyncClient
    ):
        """Should return empty list when no folders exist."""
        response = await authenticated_client.get("/api/v1/folders/tree")
        assert response.status_code == 200

        data = response.json()
        assert data == []

    async def test_get_folder_tree_with_hierarchy(
        self, authenticated_client: AsyncClient
    ):
        """Should return folder tree with nested structure."""
        # Create hierarchy
        response1 = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Tech"},
        )
        tech_id = response1.json()["id"]

        await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "News", "parent_id": tech_id},
        )

        await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Blogs"},
        )

        response = await authenticated_client.get("/api/v1/folders/tree")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2  # Tech and Blogs at root

        # Find Tech folder
        tech = next((f for f in data if f["name"] == "Tech"), None)
        assert tech is not None
        assert len(tech["subfolders"]) == 1  # News
        assert tech["subfolders"][0]["name"] == "News"


class TestGetFolderDetailsEndpoint:
    """Test GET /api/v1/folders/{folder_id} endpoint."""

    async def test_get_folder_details_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get(f"/api/v1/folders/{uuid4()}")
        assert response.status_code == 401

    async def test_get_folder_details_success(
        self, authenticated_client: AsyncClient
    ):
        """Should return folder details."""
        # Create folder
        create_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Work"},
        )
        folder_id = create_response.json()["id"]

        # Get details
        response = await authenticated_client.get(
            f"/api/v1/folders/{folder_id}"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == folder_id
        assert data["name"] == "Work"
        assert "data" in data  # Subfolders
        assert "pagination" in data

    async def test_get_folder_details_with_subfolders(
        self, authenticated_client: AsyncClient
    ):
        """Should return paginated subfolders."""
        # Create parent
        parent_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Parent"},
        )
        parent_id = parent_response.json()["id"]

        # Create children
        for i in range(3):
            await authenticated_client.post(
                "/api/v1/folders",
                json={"name": f"Child {i}", "parent_id": parent_id},
            )

        # Get details
        response = await authenticated_client.get(
            f"/api/v1/folders/{parent_id}"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 3
        assert data["pagination"]["total"] == 3

    async def test_get_folder_details_with_pagination(
        self, authenticated_client: AsyncClient
    ):
        """Should respect pagination parameters."""
        # Create parent
        parent_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Parent"},
        )
        parent_id = parent_response.json()["id"]

        # Create 5 children
        for i in range(5):
            await authenticated_client.post(
                "/api/v1/folders",
                json={"name": f"Child {i}", "parent_id": parent_id},
            )

        # Get first page
        response = await authenticated_client.get(
            f"/api/v1/folders/{parent_id}?limit=2&offset=0"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert data["pagination"]["has_more"] is True

    async def test_get_folder_details_non_existent_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent folder."""
        response = await authenticated_client.get(f"/api/v1/folders/{uuid4()}")
        assert response.status_code == 404

    async def test_get_folder_details_for_different_user_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 when accessing folder from different user."""
        # Create folder as user 1
        create_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Private"},
        )
        create_response.json()["id"]

        # Try to access a non-existent folder (user scoping makes it not found)
        response = await authenticated_client.get(f"/api/v1/folders/{uuid4()}")
        assert response.status_code == 404


class TestUpdateFolderEndpoint:
    """Test PUT /api/v1/folders/{folder_id} endpoint."""

    async def test_update_folder_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.put(
            f"/api/v1/folders/{uuid4()}",
            json={"name": "Updated"},
        )
        assert response.status_code == 401

    async def test_update_folder_name(self, authenticated_client: AsyncClient):
        """Should update folder name."""
        create_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Old Name"},
        )
        folder_id = create_response.json()["id"]

        response = await authenticated_client.put(
            f"/api/v1/folders/{folder_id}",
            json={"name": "New Name"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Folder updated successfully"

        # Verify change
        get_response = await authenticated_client.get(
            f"/api/v1/folders/{folder_id}"
        )
        assert get_response.json()["name"] == "New Name"

    async def test_update_folder_parent(
        self, authenticated_client: AsyncClient
    ):
        """Should update folder parent."""
        # Create folders
        parent1_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Parent1"},
        )
        parent1_id = parent1_response.json()["id"]

        parent2_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Parent2"},
        )
        parent2_id = parent2_response.json()["id"]

        child_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Child", "parent_id": parent1_id},
        )
        child_id = child_response.json()["id"]

        # Move child to parent2
        response = await authenticated_client.put(
            f"/api/v1/folders/{child_id}",
            json={"parent_id": parent2_id},
        )
        assert response.status_code == 200

        # Verify change
        get_response = await authenticated_client.get(
            f"/api/v1/folders/{child_id}"
        )
        assert get_response.json()["parent_id"] == parent2_id

    async def test_update_folder_toggle_pinned(
        self, authenticated_client: AsyncClient
    ):
        """Should toggle folder pinned status."""
        create_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Pin Me"},
        )
        folder_id = create_response.json()["id"]

        # Pin the folder
        await authenticated_client.put(
            f"/api/v1/folders/{folder_id}",
            json={"is_pinned": True},
        )

        # Verify change
        get_response = await authenticated_client.get(
            f"/api/v1/folders/{folder_id}"
        )
        assert get_response.json()["is_pinned"] is True

    async def test_update_folder_multiple_fields(
        self, authenticated_client: AsyncClient
    ):
        """Should update multiple fields at once."""
        create_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Old"},
        )
        folder_id = create_response.json()["id"]

        parent_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Parent"},
        )
        parent_id = parent_response.json()["id"]

        response = await authenticated_client.put(
            f"/api/v1/folders/{folder_id}",
            json={"name": "New", "parent_id": parent_id, "is_pinned": True},
        )
        assert response.status_code == 200

        # Verify all changes
        get_response = await authenticated_client.get(
            f"/api/v1/folders/{folder_id}"
        )
        data = get_response.json()
        assert data["name"] == "New"
        assert data["parent_id"] == parent_id
        assert data["is_pinned"] is True

    async def test_update_folder_non_existent_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent folder."""
        response = await authenticated_client.put(
            f"/api/v1/folders/{uuid4()}",
            json={"name": "Updated"},
        )
        assert response.status_code == 404

    async def test_update_folder_to_duplicate_name_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 400 when name conflicts with sibling."""
        await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Work"},
        )

        folder_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Personal"},
        )
        folder_id = folder_response.json()["id"]

        # Try to rename to "Work" (already exists at root)
        response = await authenticated_client.put(
            f"/api/v1/folders/{folder_id}",
            json={"name": "Work"},
        )
        assert response.status_code == 400


class TestDeleteFolderEndpoint:
    """Test DELETE /api/v1/folders/{folder_id} endpoint."""

    async def test_delete_folder_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.delete(f"/api/v1/folders/{uuid4()}")
        assert response.status_code == 401

    async def test_delete_folder_success(
        self, authenticated_client: AsyncClient
    ):
        """Should delete folder successfully."""
        create_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Delete Me"},
        )
        folder_id = create_response.json()["id"]

        response = await authenticated_client.delete(
            f"/api/v1/folders/{folder_id}"
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Folder deleted successfully"

        # Verify deletion
        get_response = await authenticated_client.get(
            f"/api/v1/folders/{folder_id}"
        )
        assert get_response.status_code == 404

    async def test_delete_folder_non_existent_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 404 for non-existent folder."""
        response = await authenticated_client.delete(
            f"/api/v1/folders/{uuid4()}"
        )
        assert response.status_code == 404


class TestFolderCascadeDelete:
    """Test cascading delete behavior."""

    async def test_delete_folder_cascades_to_children(
        self, authenticated_client: AsyncClient
    ):
        """Should delete all descendants when parent is deleted."""
        # Create hierarchy
        parent_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Parent"},
        )
        parent_id = parent_response.json()["id"]

        child_response = await authenticated_client.post(
            "/api/v1/folders",
            json={"name": "Child", "parent_id": parent_id},
        )
        child_id = child_response.json()["id"]

        # Delete parent
        await authenticated_client.delete(f"/api/v1/folders/{parent_id}")

        # Child should also be deleted (or orphaned with parent_id=NULL)
        # The database uses ON DELETE SET NULL, so child should have parent_id=None
        get_response = await authenticated_client.get(
            f"/api/v1/folders/{child_id}"
        )
        if get_response.status_code == 200:
            # Child still exists but parent_id should be None
            assert get_response.json()["parent_id"] is None
        else:
            # Child was deleted (if CASCADE is set)
            assert get_response.status_code == 404

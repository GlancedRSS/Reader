"""Integration tests for user profile and preferences endpoints."""

from uuid import uuid4

from httpx import AsyncClient


class TestGetMeEndpoint:
    """Test GET /api/v1/me endpoint."""

    async def test_get_me_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get("/api/v1/me")
        assert response.status_code == 401

    async def test_get_me_returns_user_profile(
        self, authenticated_client: AsyncClient
    ):
        """Should return authenticated user's profile."""
        response = await authenticated_client.get("/api/v1/me")
        assert response.status_code == 200

        data = response.json()
        assert "username" in data
        assert "is_admin" in data
        assert "created_at" in data
        assert "last_login" in data
        assert "first_name" in data
        assert "last_name" in data
        # These fields should NOT be in response
        assert "id" not in data
        assert "updated_at" not in data
        assert "last_active" not in data


class TestUpdateProfileEndpoint:
    """Test PUT /api/v1/me endpoint."""

    async def test_update_profile_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.put(
            "/api/v1/me", json={"first_name": "Test"}
        )
        assert response.status_code == 401

    async def test_update_profile_with_valid_data(
        self, authenticated_client: AsyncClient
    ):
        """Should update profile with valid data."""
        response = await authenticated_client.put(
            "/api/v1/me",
            json={"first_name": "John", "last_name": "Doe"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

        # Verify changes persist
        get_response = await authenticated_client.get("/api/v1/me")
        user_data = get_response.json()
        assert user_data["first_name"] == "John"
        assert user_data["last_name"] == "Doe"

    async def test_update_profile_partial_update(
        self, authenticated_client: AsyncClient
    ):
        """Should update only provided fields."""
        response = await authenticated_client.put(
            "/api/v1/me",
            json={"first_name": "Jane"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["first_name"] == "Jane"
        # last_name should remain unchanged

    async def test_update_profile_with_empty_body(
        self, authenticated_client: AsyncClient
    ):
        """Should return user without changes when no fields provided."""
        response = await authenticated_client.put("/api/v1/me", json={})
        assert response.status_code == 200

    async def test_update_profile_with_invalid_length(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for fields exceeding max length."""
        response = await authenticated_client.put(
            "/api/v1/me",
            json={"first_name": "a" * 33},  # Max is 32
        )
        assert response.status_code == 422


class TestGetPreferencesEndpoint:
    """Test GET /api/v1/me/preferences endpoint."""

    async def test_get_preferences_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.get("/api/v1/me/preferences")
        assert response.status_code == 401

    async def test_get_preferences_returns_defaults_on_first_request(
        self, authenticated_client: AsyncClient
    ):
        """Should create and return default preferences on first request."""
        response = await authenticated_client.get("/api/v1/me/preferences")
        assert response.status_code == 200

        data = response.json()
        assert data["theme"] == "system"
        assert data["show_article_thumbnails"] is True
        assert data["app_layout"] == "split"
        assert data["article_layout"] == "grid"
        assert data["font_spacing"] == "normal"
        assert data["font_size"] == "m"
        assert data["feed_sort_order"] == "recent_first"
        assert data["show_feed_favicons"] is True
        assert data["date_format"] == "relative"
        assert data["time_format"] == "12h"
        assert data["language"] == "en"
        assert data["auto_mark_as_read"] == "disabled"
        assert data["estimated_reading_time"] is True
        assert data["show_summaries"] is True


class TestUpdatePreferencesEndpoint:
    """Test PUT /api/v1/me/preferences endpoint."""

    async def test_update_preferences_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Should return 401 when not authenticated."""
        response = await async_client.put(
            "/api/v1/me/preferences",
            json={"theme": "dark"},
        )
        assert response.status_code == 401

    async def test_update_preferences_with_valid_data(
        self, authenticated_client: AsyncClient
    ):
        """Should update preferences with valid data."""
        response = await authenticated_client.put(
            "/api/v1/me/preferences",
            json={"theme": "dark", "font_size": "l"},
        )
        assert response.status_code == 200
        assert (
            response.json()["message"]
            == "User preferences updated successfully"
        )

        # Verify changes
        get_response = await authenticated_client.get("/api/v1/me/preferences")
        data = get_response.json()
        assert data["theme"] == "dark"
        assert data["font_size"] == "l"

    async def test_update_preferences_with_empty_body_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 400 when no fields provided."""
        response = await authenticated_client.put(
            "/api/v1/me/preferences",
            json={},
        )
        assert response.status_code == 400

    async def test_update_preferences_with_invalid_type_raises(
        self, authenticated_client: AsyncClient
    ):
        """Should return 422 for invalid type."""
        response = await authenticated_client.put(
            "/api/v1/me/preferences",
            json={"show_article_thumbnails": "not_a_bool"},
        )
        assert response.status_code == 422

    async def test_update_preferences_all_boolean_fields(
        self, authenticated_client: AsyncClient
    ):
        """Should update boolean preference fields."""
        response = await authenticated_client.put(
            "/api/v1/me/preferences",
            json={
                "show_article_thumbnails": False,
                "show_feed_favicons": False,
                "estimated_reading_time": False,
                "show_summaries": False,
            },
        )
        assert response.status_code == 200

        get_response = await authenticated_client.get("/api/v1/me/preferences")
        data = get_response.json()
        assert data["show_article_thumbnails"] is False
        assert data["show_feed_favicons"] is False
        assert data["estimated_reading_time"] is False
        assert data["show_summaries"] is False

    async def test_update_preferences_language_field(
        self, authenticated_client: AsyncClient
    ):
        """Should update language field (no choice constraint)."""
        response = await authenticated_client.put(
            "/api/v1/me/preferences",
            json={"language": "es"},
        )
        assert response.status_code == 200

        get_response = await authenticated_client.get("/api/v1/me/preferences")
        data = get_response.json()
        assert data["language"] == "es"


def _generate_username() -> str:
    """Generate a unique username for testing."""
    return f"testuser_{uuid4().hex[:8]}"

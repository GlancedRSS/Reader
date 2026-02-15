"""Integration tests for authentication endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


def _generate_username() -> str:
    """Generate a unique username for testing."""
    return f"testuser_{uuid4().hex[:8]}"


# =============================================================================
# Registration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient) -> None:
    """Test successful user registration."""
    username = _generate_username()
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "ValidPass123"},
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Account created successfully"


@pytest.mark.asyncio
async def test_register_invalid_username(async_client: AsyncClient) -> None:
    """Test registration with invalid username fails."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"username": "ab", "password": "ValidPass123"},
    )

    # FastAPI returns 422 for Pydantic validation errors
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_password(async_client: AsyncClient) -> None:
    """Test registration with invalid password fails."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"username": _generate_username(), "password": "weak"},
    )

    # FastAPI returns 422 for Pydantic validation errors
    assert response.status_code == 422


# =============================================================================
# Logout Tests
# =============================================================================


@pytest.mark.asyncio
async def test_logout_without_session(async_client: AsyncClient) -> None:
    """Test logout without session cookie returns 401.

    Auth middleware blocks requests without valid session.
    """
    response = await async_client.post("/api/v1/auth/logout")

    # Middleware blocks requests without valid session
    assert response.status_code == 401


# =============================================================================
# Sessions List Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_sessions_requires_auth(
    async_client: AsyncClient,
) -> None:
    """Test getting sessions requires authentication."""
    response = await async_client.get("/api/v1/auth/sessions")

    # Should require auth
    assert response.status_code == 401


# =============================================================================
# Revoke Session Tests
# =============================================================================


@pytest.mark.asyncio
async def test_revoke_session_requires_auth(
    async_client: AsyncClient,
) -> None:
    """Test revoking a session requires authentication."""
    fake_session_id = uuid4()
    response = await async_client.delete(
        f"/api/v1/auth/sessions/{fake_session_id}",
    )

    # Should require auth
    assert response.status_code == 401

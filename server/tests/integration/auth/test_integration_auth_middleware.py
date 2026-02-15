"""Integration tests for authentication middleware."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

# =============================================================================
# Public Endpoint Tests
# =============================================================================


@pytest.mark.asyncio
async def test_public_endpoint_root(async_client: AsyncClient) -> None:
    """Test root endpoint is accessible without authentication."""
    response = await async_client.get("/")
    # May return 404 if no root handler, but should not return 401
    assert response.status_code in (200, 404)


# =============================================================================
# Protected Endpoint Tests
# =============================================================================


@pytest.mark.asyncio
async def test_protected_endpoint_without_session(
    async_client: AsyncClient,
) -> None:
    """Test protected endpoint requires authentication."""
    # Sessions list requires auth
    response = await async_client.get("/api/v1/auth/sessions")
    # Should return 401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_session(
    async_client: AsyncClient,
) -> None:
    """Test protected endpoint rejects invalid session."""
    response = await async_client.get(
        "/api/v1/auth/sessions",
        cookies={"session_id": "invalid.token.string"},
    )
    # Should return 401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_expired_session(
    async_client: AsyncClient,
) -> None:
    """Test protected endpoint rejects expired session."""
    # Use a well-formed but invalid token
    fake_token = f"{uuid4()}.secrettokenvaluehere"
    response = await async_client.get(
        "/api/v1/auth/sessions",
        cookies={"session_id": fake_token},
    )
    # Should return 401
    assert response.status_code == 401


# =============================================================================
# Path Normalization Tests
# =============================================================================


@pytest.mark.asyncio
async def test_path_normalization_prevents_bypass(
    async_client: AsyncClient,
) -> None:
    """Test path normalization prevents authentication bypass."""
    # Try to access protected endpoint with encoded slashes
    response = await async_client.get("/api/v1%2Fauth/sessions")
    # Should still require authentication
    assert response.status_code in (401, 404)

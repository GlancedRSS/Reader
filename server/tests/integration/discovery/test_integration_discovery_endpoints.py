"""Integration tests for discovery endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_discover_feeds_requires_authentication(
    async_client: AsyncClient,
) -> None:
    """Test discover feeds endpoint requires authentication."""
    response = await async_client.post(
        "/api/v1/discovery",
        json={"url": "https://example.com/feed.xml"},
    )

    # Should return 401 without authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_discover_feeds_authenticated_request(
    authenticated_client: AsyncClient,
) -> None:
    """Test discover feeds endpoint accepts authenticated requests."""
    unique_url = f"https://example.com/feed-{uuid4().hex}.xml"

    response = await authenticated_client.post(
        "/api/v1/discovery",
        json={"url": unique_url},
    )

    # Should accept the request (200) even if worker might fail later
    assert response.status_code == 200

    data = response.json()
    # Check response schema
    assert "status" in data
    assert "message" in data
    # Status should be one of the valid values
    assert data["status"] in [
        "existing",
        "moved",
        "subscribed",
        "pending",
        "failed",
    ]
    # Check message is string
    assert isinstance(data["message"], str)

"""Integration tests for article endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_articles_requires_authentication(
    async_client: AsyncClient,
) -> None:
    """Test get articles endpoint requires authentication."""
    response = await async_client.get("/api/v1/articles")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_articles_authenticated_empty_response(
    authenticated_client: AsyncClient,
) -> None:
    """Test get articles returns empty list when user has no articles."""
    response = await authenticated_client.get("/api/v1/articles")

    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_get_article_by_id_requires_authentication(
    async_client: AsyncClient,
) -> None:
    """Test get article by id endpoint requires authentication."""
    article_id = uuid4()
    response = await async_client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_article_state_requires_authentication(
    async_client: AsyncClient,
) -> None:
    """Test update article state endpoint requires authentication."""
    article_id = uuid4()
    response = await async_client.put(
        f"/api/v1/articles/{article_id}",
        json={"is_read": True},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_mark_all_as_read_requires_authentication(
    async_client: AsyncClient,
) -> None:
    """Test mark all as read endpoint requires authentication."""
    response = await async_client.post(
        "/api/v1/articlesmark-as-read",
        json={"is_read": True},
    )
    assert response.status_code == 401

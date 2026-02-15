"""Unit tests for article endpoints."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.models import User
from backend.routers.article import (
    get_article,
    get_articles,
    mark_all_as_read,
    update_article_state,
)
from backend.schemas.core import PaginatedResponse, ResponseMessage
from backend.schemas.domain import (
    ArticleListResponse,
    ArticleResponse,
    ArticleStateUpdateRequest,
    MarkAllReadRequest,
)


class TestGetArticles:
    """Test get articles endpoint."""

    @pytest.mark.asyncio
    async def test_calls_article_app_with_all_params(self):
        """Should call article_app.get_articles with all filters and user."""
        user = User(id=uuid4(), username="testuser")

        mock_article_app = MagicMock()
        mock_response = MagicMock(spec=PaginatedResponse[ArticleListResponse])
        mock_article_app.get_articles = AsyncMock(return_value=mock_response)

        await get_articles(
            cursor="abc123",
            subscription_ids=[uuid4(), uuid4()],
            is_read="unread",
            tag_ids=[uuid4()],
            folder_ids=[uuid4()],
            read_later="true",
            q="search query",
            from_date=date(2024, 1, 1),
            to_date=date(2024, 12, 31),
            limit=50,
            article_app=mock_article_app,
            current_user=user,
        )

        mock_article_app.get_articles.assert_called_once()
        call_kwargs = mock_article_app.get_articles.call_args.kwargs
        assert call_kwargs["current_user"] == user
        assert call_kwargs["cursor"] == "abc123"
        assert call_kwargs["is_read"] == "unread"
        assert call_kwargs["q"] == "search query"
        assert call_kwargs["limit"] == 50

    @pytest.mark.asyncio
    async def test_returns_paginated_response(self):
        """Should return PaginatedResponse from article application."""
        user = User(id=uuid4(), username="testuser")

        mock_article_app = MagicMock()
        mock_response = MagicMock(spec=PaginatedResponse[ArticleListResponse])
        mock_article_app.get_articles = AsyncMock(return_value=mock_response)

        response = await get_articles(
            cursor=None,
            subscription_ids=None,
            is_read=None,
            tag_ids=None,
            folder_ids=None,
            read_later=None,
            q=None,
            from_date=None,
            to_date=None,
            limit=20,
            article_app=mock_article_app,
            current_user=user,
        )

        assert response == mock_response


class TestGetArticle:
    """Test get single article endpoint."""

    @pytest.mark.asyncio
    async def test_calls_article_app_with_article_id_and_user(self):
        """Should call article_app.get_article with article_id and user."""
        article_id = uuid4()
        user = User(id=uuid4(), username="testuser")

        mock_article_app = MagicMock()
        mock_response = MagicMock(spec=ArticleResponse)
        mock_article_app.get_article = AsyncMock(return_value=mock_response)

        response = await get_article(article_id, mock_article_app, user)

        mock_article_app.get_article.assert_called_once_with(article_id, user)
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_returns_article_response(self):
        """Should return ArticleResponse from application."""
        article_id = uuid4()
        user = User(id=uuid4(), username="user")

        mock_article_app = MagicMock()
        mock_response = MagicMock(spec=ArticleResponse)
        mock_article_app.get_article = AsyncMock(return_value=mock_response)

        response = await get_article(article_id, mock_article_app, user)

        assert isinstance(response, MagicMock)


class TestUpdateArticleState:
    """Test update article state endpoint."""

    @pytest.mark.asyncio
    async def test_calls_article_app_with_state_data(self):
        """Should call article_app.update_article_state with article_id, state, and user."""
        article_id = uuid4()
        user = User(id=uuid4(), username="testuser")
        state_data = ArticleStateUpdateRequest(is_read=True, read_later=False)

        mock_article_app = MagicMock()
        mock_response = ResponseMessage(message="Article updated")
        mock_article_app.update_article_state = AsyncMock(
            return_value=mock_response
        )

        response = await update_article_state(
            article_id, state_data, mock_article_app, user
        )

        mock_article_app.update_article_state.assert_called_once_with(
            article_id, state_data, user
        )
        assert response.message == "Article updated"

    @pytest.mark.asyncio
    async def test_passes_state_request_to_application(self):
        """Should pass state_data to article application."""
        article_id = uuid4()
        user = User(id=uuid4(), username="user")
        state_data = ArticleStateUpdateRequest(
            is_read=False, tags_to_add=[uuid4()]
        )

        mock_article_app = MagicMock()
        mock_article_app.update_article_state = AsyncMock(
            return_value=MagicMock()
        )

        await update_article_state(
            article_id, state_data, mock_article_app, user
        )

        call_args = mock_article_app.update_article_state.call_args
        assert call_args[0][1] == state_data


class TestMarkAllAsRead:
    """Test mark all as read endpoint."""

    @pytest.mark.asyncio
    async def test_calls_article_app_with_request_and_user(self):
        """Should call article_app.mark_all_as_read with request and user."""
        user = User(id=uuid4(), username="testuser")
        request_data = MarkAllReadRequest(
            is_read=True, subscription_ids=[uuid4()]
        )

        mock_article_app = MagicMock()
        mock_response = ResponseMessage(message="Articles marked as read")
        mock_article_app.mark_all_as_read = AsyncMock(
            return_value=mock_response
        )

        response = await mark_all_as_read(request_data, mock_article_app, user)

        mock_article_app.mark_all_as_read.assert_called_once_with(
            request_data, user
        )
        assert response.message == "Articles marked as read"

    @pytest.mark.asyncio
    async def test_passes_user_from_dependency(self):
        """Should pass current_user from dependency injection."""
        user = User(id=uuid4(), username="user")
        request_data = MarkAllReadRequest(is_read=False)

        mock_article_app = MagicMock()
        mock_article_app.mark_all_as_read = AsyncMock(return_value=MagicMock())

        await mark_all_as_read(request_data, mock_article_app, user)

        call_args = mock_article_app.mark_all_as_read.call_args
        assert call_args[0][1] == user

    @pytest.mark.asyncio
    async def test_handles_empty_subscription_ids(self):
        """Should handle request with no subscription filters."""
        user = User(id=uuid4(), username="testuser")
        request_data = MarkAllReadRequest(is_read=True, subscription_ids=None)

        mock_article_app = MagicMock()
        mock_response = ResponseMessage(message="All articles marked as read")
        mock_article_app.mark_all_as_read = AsyncMock(
            return_value=mock_response
        )

        response = await mark_all_as_read(request_data, mock_article_app, user)

        mock_article_app.mark_all_as_read.assert_called_once()
        assert response.message == "All articles marked as read"

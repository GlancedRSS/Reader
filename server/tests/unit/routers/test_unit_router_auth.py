"""Unit tests for authentication endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import Request, Response

from backend.models import User
from backend.routers.auth import (
    change_password,
    get_user_sessions,
    login,
    logout,
    register,
    revoke_session,
)
from backend.schemas.core import ResponseMessage
from backend.schemas.core.common import ListResponse
from backend.schemas.domain.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RegistrationRequest,
)


class TestRegister:
    """Test user registration endpoint."""

    @pytest.mark.asyncio
    async def test_calls_auth_app_register(self):
        """Should call auth_app.register with user data."""
        user_data = RegistrationRequest(
            username="newuser", password="SecurePass123!"
        )
        mock_db = MagicMock()
        mock_auth_app = MagicMock()
        mock_response = ResponseMessage(message="User registered")
        mock_auth_app.register = AsyncMock(return_value=mock_response)

        # Patch AuthApplication constructor
        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            response = await register(user_data, mock_db)

        mock_auth_app.register.assert_called_once_with(user_data)
        assert response.message == "User registered"

    @pytest.mark.asyncio
    async def test_returns_response_message(self):
        """Should return ResponseMessage from auth application."""
        user_data = RegistrationRequest(username="test", password="pass12345")
        mock_db = MagicMock()
        mock_auth_app = MagicMock()
        mock_response = ResponseMessage(message="Registration successful")
        mock_auth_app.register = AsyncMock(return_value=mock_response)

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            response = await register(user_data, mock_db)

        assert isinstance(response, ResponseMessage)


class TestLogin:
    """Test user login endpoint."""

    @pytest.mark.asyncio
    async def test_calls_auth_app_login_and_sets_cookies(self):
        """Should call auth_app.login and set session cookies."""
        user_data = LoginRequest(username="testuser", password="password123")
        mock_request = MagicMock(spec=Request)
        mock_response = MagicMock(spec=Response)
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_session_app = MagicMock()

        mock_result = ResponseMessage(message="Login successful")
        mock_auth_app.login = AsyncMock(
            return_value=(mock_result, (uuid4(), uuid4()))
        )

        mock_cookies = {
            "session_cookie": {"key": "session", "value": "abc123"},
            "csrf_cookie": {"key": "csrf", "value": "xyz789"},
        }
        mock_session_app.generate_session_cookies = MagicMock(
            return_value=mock_cookies
        )

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            with patch(
                "backend.routers.auth.CookieManager",
                return_value=mock_session_app,
            ):
                await login(user_data, mock_request, mock_response, mock_db)

        mock_auth_app.login.assert_called_once_with(user_data, mock_request)
        mock_session_app.generate_session_cookies.assert_called_once()
        mock_response.set_cookie.assert_any_call(
            **mock_cookies["session_cookie"]
        )
        mock_response.set_cookie.assert_any_call(**mock_cookies["csrf_cookie"])

    @pytest.mark.asyncio
    async def test_returns_login_result(self):
        """Should return result from auth_app.login."""
        user_data = LoginRequest(username="test", password="pass")
        mock_request = MagicMock(spec=Request)
        mock_response = MagicMock(spec=Response)
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_session_app = MagicMock()

        mock_result = ResponseMessage(message="Welcome back!")
        mock_auth_app.login = AsyncMock(
            return_value=(mock_result, (uuid4(), uuid4()))
        )
        mock_session_app.generate_session_cookies = MagicMock(
            return_value={"session_cookie": {}, "csrf_cookie": {}}
        )

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            with patch(
                "backend.routers.auth.CookieManager",
                return_value=mock_session_app,
            ):
                response = await login(
                    user_data, mock_request, mock_response, mock_db
                )

        assert response.message == "Welcome back!"


class TestLogout:
    """Test user logout endpoint."""

    @pytest.mark.asyncio
    async def test_calls_auth_app_logout_and_clears_cookies(self):
        """Should call auth_app.logout and clear cookies."""
        mock_request = MagicMock(spec=Request)
        mock_response = MagicMock(spec=Response)
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_session_app = MagicMock()

        mock_result = ResponseMessage(message="Logged out")
        mock_auth_app.logout = AsyncMock(return_value=mock_result)

        mock_clear_cookies = {
            "session_cookie": {"key": "session"},
            "csrf_cookie": {"key": "csrf"},
        }
        mock_session_app.generate_clear_cookies = MagicMock(
            return_value=mock_clear_cookies
        )

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            with patch(
                "backend.routers.auth.CookieManager",
                return_value=mock_session_app,
            ):
                await logout(mock_request, mock_response, mock_db)

        mock_auth_app.logout.assert_called_once_with(mock_request)
        mock_session_app.generate_clear_cookies.assert_called_once()
        mock_response.delete_cookie.assert_any_call(
            **mock_clear_cookies["session_cookie"]
        )
        mock_response.delete_cookie.assert_any_call(
            **mock_clear_cookies["csrf_cookie"]
        )

    @pytest.mark.asyncio
    async def test_returns_logout_result(self):
        """Should return result from auth_app.logout."""
        mock_request = MagicMock(spec=Request)
        mock_response = MagicMock(spec=Response)
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_session_app = MagicMock()

        mock_result = ResponseMessage(message="Logged out successfully")
        mock_auth_app.logout = AsyncMock(return_value=mock_result)
        mock_session_app.generate_clear_cookies = MagicMock(
            return_value={"session_cookie": {}, "csrf_cookie": {}}
        )

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            with patch(
                "backend.routers.auth.CookieManager",
                return_value=mock_session_app,
            ):
                response = await logout(mock_request, mock_response, mock_db)

        assert response.message == "Logged out successfully"


class TestChangePassword:
    """Test password change endpoint."""

    @pytest.mark.asyncio
    async def test_calls_auth_app_change_password(self):
        """Should call auth_app.change_password with user data."""
        password_data = PasswordChangeRequest(
            current_password="oldpass", new_password="newpass123"
        )
        user = User(id=uuid4(), username="testuser")
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_response = ResponseMessage(message="Password changed")
        mock_auth_app.change_password = AsyncMock(return_value=mock_response)

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            response = await change_password(password_data, user, mock_db)

        mock_auth_app.change_password.assert_called_once_with(
            password_data, user
        )
        assert response.message == "Password changed"

    @pytest.mark.asyncio
    async def test_passes_current_user_to_auth_app(self):
        """Should pass current_user to auth application."""
        password_data = PasswordChangeRequest(
            current_password="oldpass123", new_password="newpass456"
        )
        user = User(id=uuid4(), username="user")
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_auth_app.change_password = AsyncMock(return_value=MagicMock())

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            await change_password(password_data, user, mock_db)

        call_args = mock_auth_app.change_password.call_args
        assert call_args[0][1] == user


class TestGetUserSessions:
    """Test get user sessions endpoint."""

    @pytest.mark.asyncio
    async def test_calls_auth_app_get_sessions(self):
        """Should call auth_app.get_sessions with user and session_id."""
        mock_request = MagicMock(spec=Request)
        user = User(id=uuid4(), username="testuser")
        mock_db = MagicMock()

        session_id = uuid4()
        mock_request.cookies.get.return_value = "session_token_123"

        mock_auth_app = MagicMock()
        mock_response = MagicMock(spec=ListResponse)
        mock_auth_app.get_current_session_id = AsyncMock(
            return_value=session_id
        )
        mock_auth_app.get_sessions = AsyncMock(return_value=mock_response)

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            with patch("backend.routers.auth.settings") as mock_settings:
                mock_settings.session_cookie_name = "session_id"
                response = await get_user_sessions(mock_request, user, mock_db)

        mock_auth_app.get_sessions.assert_called_once_with(user, session_id)
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_handles_missing_session_cookie(self):
        """Should handle missing session cookie gracefully."""
        mock_request = MagicMock(spec=Request)
        user = User(id=uuid4(), username="testuser")
        mock_db = MagicMock()

        mock_request.cookies.get.return_value = None

        mock_auth_app = MagicMock()
        mock_response = MagicMock(spec=ListResponse)
        mock_auth_app.get_sessions = AsyncMock(return_value=mock_response)

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            with patch("backend.routers.auth.settings") as mock_settings:
                mock_settings.session_cookie_name = "session_id"
                response = await get_user_sessions(mock_request, user, mock_db)

        mock_auth_app.get_current_session_id.assert_not_called()
        mock_auth_app.get_sessions.assert_called_once_with(user, None)
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_handles_invalid_session_token(self):
        """Should handle ValueError from get_current_session_id."""
        mock_request = MagicMock(spec=Request)
        user = User(id=uuid4(), username="testuser")
        mock_db = MagicMock()

        mock_request.cookies.get.return_value = "invalid_token"

        mock_auth_app = MagicMock()
        mock_response = MagicMock(spec=ListResponse)
        mock_auth_app.get_current_session_id = AsyncMock(
            side_effect=ValueError("Invalid")
        )
        mock_auth_app.get_sessions = AsyncMock(return_value=mock_response)

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            with patch("backend.routers.auth.settings") as mock_settings:
                mock_settings.session_cookie_name = "session_id"
                response = await get_user_sessions(mock_request, user, mock_db)

        mock_auth_app.get_sessions.assert_called_once_with(user, None)
        assert response == mock_response


class TestRevokeSession:
    """Test revoke session endpoint."""

    @pytest.mark.asyncio
    async def test_calls_auth_app_revoke_session(self):
        """Should call auth_app.revoke_session with session_id and user."""
        session_id = uuid4()
        user = User(id=uuid4(), username="testuser")
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_response = ResponseMessage(message="Session revoked")
        mock_auth_app.revoke_session = AsyncMock(return_value=mock_response)

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            response = await revoke_session(session_id, user, mock_db)

        mock_auth_app.revoke_session.assert_called_once_with(session_id, user)
        assert response.message == "Session revoked"

    @pytest.mark.asyncio
    async def test_passes_session_id_from_path(self):
        """Should pass session_id from URL path to auth application."""
        session_id = uuid4()
        user = User(id=uuid4(), username="user")
        mock_db = MagicMock()

        mock_auth_app = MagicMock()
        mock_auth_app.revoke_session = AsyncMock(return_value=MagicMock())

        with patch(
            "backend.routers.auth.AuthApplication", return_value=mock_auth_app
        ):
            await revoke_session(session_id, user, mock_db)

        call_args = mock_auth_app.revoke_session.call_args
        assert call_args[0][0] == session_id

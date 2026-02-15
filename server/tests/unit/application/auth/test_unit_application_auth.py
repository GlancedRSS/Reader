"""Unit tests for AuthApplication."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.auth import AuthApplication
from backend.domain import InvalidPasswordError
from backend.models import User
from backend.schemas.domain.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RegistrationRequest,
)


class TestAuthApplicationRegister:
    """Test user registration operations."""

    @pytest.mark.asyncio
    async def test_register_assigns_admin_to_first_user(
        self, db_session: AsyncSession
    ):
        """Should assign admin privileges to first registered user."""
        mock_user_repo = MagicMock()
        mock_user_repo.username_exists = AsyncMock(return_value=False)
        mock_user_repo.count_users = AsyncMock(return_value=0)
        mock_user_repo.create_user = AsyncMock()
        created_user = MagicMock()
        created_user.id = uuid4()
        created_user.username = "firstuser"
        mock_user_repo.create_user.return_value = created_user

        mock_validation = MagicMock()
        mock_validation.validate_username_format = MagicMock(
            return_value="testuser"
        )
        mock_validation.validate_password_format = MagicMock()
        mock_validation.validate_username_unique = MagicMock()

        with patch(
            "backend.application.auth.auth.UserRepository",
            return_value=mock_user_repo,
        ):
            app = AuthApplication(db_session)
            app.validation = mock_validation

            response = await app.register(
                RegistrationRequest(username="testuser", password="TestPass123")
            )

        assert "created successfully" in response.message.lower()
        mock_user_repo.create_user.assert_called_once()
        # Verify is_admin=True for first user
        call_kwargs = mock_user_repo.create_user.call_args[1]
        assert call_kwargs["is_admin"] is True

    @pytest.mark.asyncio
    async def test_register_does_not_assign_admin_to_subsequent_users(
        self, db_session: AsyncSession
    ):
        """Should not assign admin privileges to subsequent users."""
        mock_user_repo = MagicMock()
        mock_user_repo.username_exists = AsyncMock(return_value=False)
        mock_user_repo.count_users = AsyncMock(return_value=5)  # Not first user
        mock_user_repo.create_user = AsyncMock()

        mock_validation = MagicMock()
        mock_validation.validate_username_format = MagicMock(
            return_value="testuser"
        )
        mock_validation.validate_password_format = MagicMock()
        mock_validation.validate_username_unique = MagicMock()

        with patch(
            "backend.application.auth.auth.UserRepository",
            return_value=mock_user_repo,
        ):
            app = AuthApplication(db_session)
            app.validation = mock_validation

            await app.register(
                RegistrationRequest(username="testuser", password="TestPass123")
            )

        call_kwargs = mock_user_repo.create_user.call_args[1]
        assert call_kwargs["is_admin"] is False

    @pytest.mark.asyncio
    async def test_register_raises_409_when_username_exists(
        self, db_session: AsyncSession
    ):
        """Should raise 409 CONFLICT when username already exists."""
        mock_user_repo = MagicMock()
        mock_user_repo.username_exists = AsyncMock(return_value=True)
        mock_user_repo.count_users = AsyncMock(return_value=0)
        mock_user_repo.create_user = AsyncMock()

        mock_validation = MagicMock()
        mock_validation.validate_username_format = MagicMock(
            return_value="takenuser"
        )
        mock_validation.validate_password_format = MagicMock()
        mock_validation.validate_username_unique = MagicMock(
            side_effect=ValueError("Username 'takenuser' already exists")
        )

        with patch(
            "backend.application.auth.auth.UserRepository",
            return_value=mock_user_repo,
        ):
            app = AuthApplication(db_session)
            app.validation = mock_validation

            with pytest.raises(HTTPException) as exc_info:
                await app.register(
                    RegistrationRequest(
                        username="takenuser", password="TestPass123"
                    )
                )

        assert exc_info.value.status_code == 409


class TestAuthApplicationLogin:
    """Test user login operations."""

    @pytest.mark.asyncio
    async def test_login_handles_session_limit_and_revokes_oldest(
        self, db_session: AsyncSession
    ):
        """Should revoke oldest session when session limit is reached."""
        user_id = uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id
        mock_user.username = "testuser"
        mock_user.last_login = MagicMock()

        mock_user_repo = MagicMock()
        mock_user_repo.find_by_username = AsyncMock(return_value=mock_user)
        mock_user_repo.update_user = AsyncMock()

        mock_session_repo = MagicMock()
        mock_session_repo.get_active_session_count = AsyncMock(
            return_value=6
        )  # Above limit
        mock_session_repo.revoke_oldest_session = AsyncMock(return_value=True)
        mock_session = MagicMock()
        mock_session.session_id = uuid4()
        mock_session_repo.create_session = AsyncMock(
            return_value=(mock_session, "token123")
        )

        mock_request = MagicMock(spec=Request)
        mock_request.headers = MagicMock(get=lambda x: "TestAgent")

        with patch(
            "backend.application.auth.auth.UserRepository",
            return_value=mock_user_repo,
        ):
            with patch(
                "backend.infrastructure.repositories.session.SessionRepository",
                return_value=mock_session_repo,
            ):
                with patch(
                    "backend.infrastructure.auth.ip_utils.IPUtils.get_client_ip",
                    return_value="127.0.0.1",
                ):
                    with patch(
                        "backend.application.auth.auth.generate_csrf_token",
                        return_value="csrf123",
                    ):
                        app = AuthApplication(db_session)
                        # Mock verify_credentials to bypass password verification
                        app.auth_domain.verify_credentials = MagicMock()

                        await app.login(
                            LoginRequest(
                                username="testuser", password="TestPass123"
                            ),
                            mock_request,
                        )

        # Verify oldest session was revoked
        mock_session_repo.revoke_oldest_session.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_login_returns_401_for_nonexistent_user(
        self, db_session: AsyncSession
    ):
        """Should return 401 UNAUTHORIZED when user doesn't exist."""
        mock_user_repo = MagicMock()
        mock_user_repo.find_by_username = AsyncMock(return_value=None)

        mock_request = MagicMock(spec=Request)

        with patch(
            "backend.application.auth.auth.UserRepository",
            return_value=mock_user_repo,
        ):
            app = AuthApplication(db_session)

            with pytest.raises(HTTPException) as exc_info:
                await app.login(
                    LoginRequest(
                        username="nonexistent", password="TestPass123"
                    ),
                    mock_request,
                )

        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in exc_info.value.detail


class TestAuthApplicationLogout:
    """Test user logout operations."""

    @pytest.mark.asyncio
    async def test_logout_logs_warning_without_session_cookie(
        self, db_session: AsyncSession
    ):
        """Should log warning when logout attempted without session cookie."""
        mock_request = MagicMock(spec=Request)
        mock_request.cookies.get = MagicMock(return_value=None)

        with patch(
            "backend.application.auth.auth.revoke_session_cookie",
            AsyncMock(return_value=True),
        ):
            app = AuthApplication(db_session)

            response = await app.logout(mock_request)

        assert "Successfully logged out" in response.message

    @pytest.mark.asyncio
    async def test_logout_logs_warning_with_invalid_session(
        self, db_session: AsyncSession
    ):
        """Should log warning when logout attempted with invalid session."""
        mock_request = MagicMock(spec=Request)
        mock_request.cookies.get = MagicMock(return_value="invalid_token")

        with patch(
            "backend.application.auth.auth.revoke_session_cookie",
            AsyncMock(return_value=False),
        ):
            app = AuthApplication(db_session)

            response = await app.logout(mock_request)

        assert "Successfully logged out" in response.message


class TestAuthApplicationChangePassword:
    """Test password change operations."""

    @pytest.mark.asyncio
    async def test_change_password_revokes_all_sessions(
        self, db_session: AsyncSession
    ):
        """Should revoke all user sessions after successful password change."""
        user_id = uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id

        mock_session_repo = MagicMock()
        mock_session_repo.revoke_all_user_sessions = AsyncMock()

        app = AuthApplication(db_session)
        app.session_repository = mock_session_repo
        app.auth_domain = MagicMock()
        app.auth_domain.change_user_password = MagicMock()

        response = await app.change_password(
            PasswordChangeRequest(
                current_password="OldPass123", new_password="NewPass456"
            ),
            mock_user,
        )

        assert "Password changed successfully" in response.message
        mock_session_repo.revoke_all_user_sessions.assert_called_once_with(
            user_id
        )

    @pytest.mark.asyncio
    async def test_change_password_raises_400_for_invalid_current_password(
        self, db_session: AsyncSession
    ):
        """Should raise 400 BAD REQUEST when current password is invalid."""
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()

        app = AuthApplication(db_session)
        app.auth_domain = MagicMock()
        app.auth_domain.change_user_password = MagicMock(
            side_effect=InvalidPasswordError("Wrong password")
        )

        with pytest.raises(HTTPException) as exc_info:
            await app.change_password(
                PasswordChangeRequest(
                    current_password="WrongPass123", new_password="NewPass456"
                ),
                mock_user,
            )

        assert exc_info.value.status_code == 400
        assert "Wrong password" in exc_info.value.detail


class TestAuthApplicationGetSessions:
    """Test get sessions list operation."""

    @pytest.mark.asyncio
    async def test_get_sessions_formats_ip_address_as_none_when_null(
        self, db_session: AsyncSession
    ):
        """Should format ip_address as None when session.ip_address is None."""
        user_id = uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id

        mock_session = MagicMock()
        mock_session.session_id = uuid4()
        mock_session.created_at = MagicMock()
        mock_session.last_used = MagicMock()
        mock_session.expires_at = MagicMock()
        mock_session.user_agent = "TestAgent"
        mock_session.ip_address = None  # No IP address

        mock_session_repo = MagicMock()
        mock_session_repo.get_user_sessions = AsyncMock(
            return_value=[mock_session]
        )

        app = AuthApplication(db_session)
        app.session_repository = mock_session_repo

        response = await app.get_sessions(mock_user, MagicMock())

        assert len(response.data) == 1
        assert response.data[0].ip_address is None


class TestAuthApplicationRevokeSession:
    """Test session revocation operations."""

    @pytest.mark.asyncio
    async def test_revoke_session_raises_404_when_session_not_found(
        self, db_session: AsyncSession
    ):
        """Should raise 404 NOT FOUND when session doesn't exist."""
        user_id = uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id

        mock_session_repo = MagicMock()
        mock_session_repo.revoke_session_by_id = AsyncMock(return_value=0)

        app = AuthApplication(db_session)
        app.session_repository = mock_session_repo

        with pytest.raises(HTTPException) as exc_info:
            await app.revoke_session(uuid4(), mock_user)

        assert exc_info.value.status_code == 404
        assert "Session not found" in exc_info.value.detail


class TestAuthApplicationGetCurrentSessionId:
    """Test get current session ID operation."""

    @pytest.mark.asyncio
    async def test_get_current_session_id_raises_value_error_for_invalid_session(
        self, db_session: AsyncSession
    ):
        """Should raise ValueError when session is invalid or expired."""
        app = AuthApplication(db_session)

        with patch(
            "backend.application.auth.auth.verify_session_cookie",
            AsyncMock(return_value=None),
        ):
            with pytest.raises(ValueError, match="Invalid or expired session"):
                await app.get_current_session_id("invalid_token")

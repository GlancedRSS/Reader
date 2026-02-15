"""Unit tests for AuthDomain - business rules for authentication."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from backend.domain.auth import AuthDomain
from backend.domain.auth.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
)
from backend.domain.constants import MAX_ACTIVE_SESSIONS
from backend.infrastructure.auth.security import PasswordHasher
from backend.models import User


class TestAuthDomainInit:
    """Test AuthDomain initialization."""

    def test_initializes_with_password_hasher(self):
        """Should initialize with a PasswordHasher instance."""
        mock_hasher = MagicMock(spec=PasswordHasher)
        domain = AuthDomain(password_hasher=mock_hasher)

        assert domain.password_hasher == mock_hasher

    def test_initializes_with_default_password_hasher(self):
        """Should initialize with provided password hasher (or None)."""
        domain = AuthDomain(password_hasher=None)

        # AuthDomain doesn't create a default, it just stores what's passed
        assert domain.password_hasher is None


class TestUpdateLastLogin:
    """Test update_last_login method."""

    def test_updates_last_login_timestamp(self):
        """Should update user's last_login to current UTC time."""
        mock_user = MagicMock(spec=User)
        mock_user.last_login = None

        domain = AuthDomain(password_hasher=MagicMock())
        domain.update_last_login(mock_user)

        assert mock_user.last_login is not None
        assert isinstance(mock_user.last_login, datetime)
        # Check it's recent (within last second)
        assert (datetime.now(UTC) - mock_user.last_login).total_seconds() < 1


class TestVerifyCredentials:
    """Test verify_credentials method."""

    def test_verify_credentials_success(self):
        """Should pass when password matches hash."""
        mock_user = MagicMock(spec=User)
        mock_user.password_hash = "correct_hash"
        mock_hasher = MagicMock()
        mock_hasher.verify_password.return_value = True

        domain = AuthDomain(password_hasher=mock_hasher)
        # Should not raise - password matches
        domain.verify_credentials(mock_user, "correct_password")

        mock_hasher.verify_password.assert_called_once_with(
            "correct_password", "correct_hash"
        )

    def test_verify_credentials_no_hash_raises(self):
        """Should raise InvalidCredentialsError when user has no password_hash."""
        mock_user = MagicMock(spec=User)
        mock_user.password_hash = None
        mock_hasher = MagicMock()

        domain = AuthDomain(password_hasher=mock_hasher)

        with pytest.raises(InvalidCredentialsError):
            domain.verify_credentials(mock_user, "password")

    def test_verify_credentials_wrong_password_raises(self):
        """Should raise InvalidCredentialsError when password doesn't match."""
        mock_user = MagicMock(spec=User)
        mock_user.password_hash = "stored_hash"
        mock_hasher = MagicMock()
        mock_hasher.verify_password.return_value = False

        domain = AuthDomain(password_hasher=mock_hasher)

        with pytest.raises(InvalidCredentialsError):
            domain.verify_credentials(mock_user, "wrong_password")

        mock_hasher.verify_password.assert_called_once_with(
            "wrong_password", "stored_hash"
        )


class TestChangeUserPassword:
    """Test change_user_password method."""

    def test_change_password_success(self):
        """Should hash and set new password when current password is valid."""
        mock_user = MagicMock(spec=User)
        mock_user.password_hash = "old_hash"
        mock_hasher = MagicMock()
        mock_hasher.hash_password.return_value = "new_hash"

        domain = AuthDomain(password_hasher=mock_hasher)
        domain.change_user_password(mock_user, "old_password", "new_password")

        assert mock_user.password_hash == "new_hash"
        mock_hasher.hash_password.assert_called_once_with("new_password")

    def test_change_password_invalid_current_raises(self):
        """Should raise InvalidPasswordError when current password is invalid."""
        mock_user = MagicMock(spec=User)
        mock_user.password_hash = "stored_hash"
        mock_hasher = MagicMock()
        mock_hasher.verify_password.return_value = False

        domain = AuthDomain(password_hasher=mock_hasher)

        with pytest.raises(InvalidPasswordError) as exc_info:
            domain.change_user_password(
                mock_user, "wrong_current", "new_password"
            )

        assert "Invalid current password" in str(exc_info.value)


class TestCheckSessionLimit:
    """Test check_session_limit method."""

    def test_check_session_limit_below_max(self):
        """Should return False when below session limit."""
        domain = AuthDomain(password_hasher=MagicMock())

        result = domain.check_session_limit(MAX_ACTIVE_SESSIONS - 1)

        assert result is False

    def test_check_session_limit_at_max(self):
        """Should return True when exactly at session limit (>= condition)."""
        domain = AuthDomain(password_hasher=MagicMock())

        result = domain.check_session_limit(MAX_ACTIVE_SESSIONS)

        # The logic uses >=, so at max it returns True
        assert result is True

    def test_check_session_limit_above_max(self):
        """Should return True when above session limit."""
        domain = AuthDomain(password_hasher=MagicMock())

        result = domain.check_session_limit(MAX_ACTIVE_SESSIONS + 1)

        assert result is True

    def test_check_session_limit_exactly_max_plus_one(self):
        """Should return True when exceeding by one."""
        domain = AuthDomain(password_hasher=MagicMock())

        result = domain.check_session_limit(MAX_ACTIVE_SESSIONS + 1)

        assert result is True

    def test_first_user_is_admin_constant(self):
        """Should have FIRST_USER_IS_ADMIN constant set to True."""
        domain = AuthDomain(password_hasher=MagicMock())

        assert domain.FIRST_USER_IS_ADMIN is True

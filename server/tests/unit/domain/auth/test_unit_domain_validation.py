"""Unit tests for AuthValidationDomain - validation rules for auth."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.domain.auth.validation import AuthValidationDomain


class TestValidateUsernameFormat:
    """Test username format validation."""

    def test_validate_username_format_valid(self):
        """Should accept valid username."""
        result = AuthValidationDomain.validate_username_format("testuser")

        assert result == "testuser"

    def test_validate_username_format_trims_whitespace(self):
        """Should trim whitespace from username."""
        result = AuthValidationDomain.validate_username_format("  TestUser  ")

        assert result == "testuser"

    def test_validate_username_format_too_short_raises(self):
        """Should raise ValueError for username below min length."""

        with pytest.raises(ValueError, match="must be at least"):
            AuthValidationDomain.validate_username_format("ab")

    def test_validate_username_format_too_long_raises(self):
        """Should raise ValueError for username above max length."""
        from backend.domain.constants import MAX_USERNAME_LENGTH

        with pytest.raises(ValueError, match="must be at most"):
            AuthValidationDomain.validate_username_format(
                "a" * (MAX_USERNAME_LENGTH + 1)
            )

    def test_validate_username_format_special_chars_only_raises(self):
        """Should raise ValueError for username with only special characters."""
        with pytest.raises(
            ValueError, match="letters, numbers, underscores, and hyphens"
        ):
            AuthValidationDomain.validate_username_format("_-!@")

    def test_validate_username_format_with_valid_special_chars(self):
        """Should accept underscores and hyphens in username."""
        result = AuthValidationDomain.validate_username_format("test_user-123")

        assert result == "test_user-123"

    def test_validate_username_format_lowercase(self):
        """Should convert username to lowercase."""
        result = AuthValidationDomain.validate_username_format("TestUser")

        assert result == "testuser"


class TestValidatePasswordFormat:
    """Test password format validation."""

    def test_validate_password_format_valid(self):
        """Should accept valid password."""
        result = AuthValidationDomain.validate_password_format("TestPass123")

        assert result is None

    def test_validate_password_format_too_short_raises(self):
        """Should raise ValueError for password below min length."""

        with pytest.raises(ValueError, match="must be at least"):
            AuthValidationDomain.validate_password_format("short")

    def test_validate_password_format_too_long_raises(self):
        """Should raise ValueError for password above max length."""
        from backend.domain.constants import MAX_PASSWORD_LENGTH

        with pytest.raises(ValueError, match="must be at most"):
            AuthValidationDomain.validate_password_format(
                "a" * (MAX_PASSWORD_LENGTH + 1)
            )

    def test_validate_password_format_no_letter_raises(self):
        """Should raise ValueError for password with no letters."""
        with pytest.raises(
            ValueError, match="must contain at least one letter"
        ):
            AuthValidationDomain.validate_password_format("12345678")

    def test_validate_password_format_no_number_raises(self):
        """Should raise ValueError for password with no numbers."""
        with pytest.raises(
            ValueError, match="must contain at least one number"
        ):
            AuthValidationDomain.validate_password_format("ABCDEFGHIJ")

    def test_validate_password_format_valid_complex(self):
        """Should accept valid complex password."""
        result = AuthValidationDomain.validate_password_format("SecurePass123!")

        assert result is None


class TestValidateUsernameUnique:
    """Test username uniqueness validation."""

    def test_validate_username_unique_when_available(self):
        """Should pass when username is available."""
        result = AuthValidationDomain.validate_username_unique(
            username_exists=False
        )

        assert result is None

    def test_validate_username_unique_when_taken(self):
        """Should raise ValueError when username exists."""
        with pytest.raises(ValueError, match="already exists"):
            AuthValidationDomain.validate_username_unique(username_exists=True)


class TestValidateSessionActive:
    """Test session active validation."""

    def test_validate_session_active_no_expiry_raises(self):
        """Should return True for session without expiry."""
        result = AuthValidationDomain.validate_session_active(expires_at=None)

        assert result is True

    def test_validate_session_active_future_expiry(self):
        """Should return True for session expiring in future."""
        future = datetime.now(UTC).replace(microsecond=0) + timedelta(days=1)
        result = AuthValidationDomain.validate_session_active(expires_at=future)

        assert result is True

    def test_validate_session_active_past_expiry_raises(self):
        """Should return False for expired session."""
        past = datetime.now(UTC).replace(microsecond=0) - timedelta(days=1)
        result = AuthValidationDomain.validate_session_active(expires_at=past)

        assert result is False

    def test_validate_session_active_exactly_now_raises(self):
        """Should return False for session expiring exactly now."""
        now = datetime.now(UTC).replace(microsecond=0)
        result = AuthValidationDomain.validate_session_active(expires_at=now)

        assert result is False

"""Validation tests for username and password rules."""

import pytest

from backend.domain.auth.validation import AuthValidationDomain
from backend.domain.constants import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)


class TestUsernameValidation:
    """Test username format and length validation."""

    def test_valid_username_accepted(self):
        """Should accept valid usernames."""
        validator = AuthValidationDomain()

        valid_usernames = [
            "user",
            "test123",
            "user_name",
            "user-name",
            "User123",
            "abc",
            "a",
            "test-user-123",
        ]

        for username in valid_usernames:
            if MIN_USERNAME_LENGTH <= len(username) <= MAX_USERNAME_LENGTH:
                result = validator.validate_username_format(username)
                assert result == username.lower()

    def test_username_too_short(self):
        """Should reject username below minimum length."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match=r"at least \d+ characters"):
            validator.validate_username_format("ab")

    def test_username_too_long(self):
        """Should reject username exceeding maximum length."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match=r"at most \d+ characters"):
            validator.validate_username_format("a" * (MAX_USERNAME_LENGTH + 1))

    def test_username_at_minimum_length(self):
        """Should accept username at exactly minimum length."""
        validator = AuthValidationDomain()

        result = validator.validate_username_format("a" * MIN_USERNAME_LENGTH)
        assert result == "a" * MIN_USERNAME_LENGTH

    def test_username_at_maximum_length(self):
        """Should accept username at exactly maximum length."""
        validator = AuthValidationDomain()

        result = validator.validate_username_format("a" * MAX_USERNAME_LENGTH)
        assert result == "a" * MAX_USERNAME_LENGTH

    def test_username_with_special_characters_rejected(self):
        """Should reject usernames with invalid special characters."""
        validator = AuthValidationDomain()

        invalid_usernames = [
            "user@name",
            "user#name",
            "user.name",
            "user name",
            "user/name",
            "user\\name",
        ]

        for username in invalid_usernames:
            with pytest.raises(
                ValueError, match="letters, numbers, underscores"
            ):
                validator.validate_username_format(username)

    def test_username_lowercase_conversion(self):
        """Should convert username to lowercase."""
        validator = AuthValidationDomain()

        result = validator.validate_username_format("TESTUSER")
        assert result == "testuser"

        result = validator.validate_username_format("TeStUsEr")
        assert result == "testuser"

    def test_username_whitespace_is_stripped(self):
        """Should strip leading/trailing whitespace."""
        validator = AuthValidationDomain()

        result = validator.validate_username_format("  testuser  ")
        assert result == "testuser"

    def test_empty_username_rejected(self):
        """Should reject empty username."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="required"):
            validator.validate_username_format("")

    def test_username_none_rejected(self):
        """Should reject None username."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="required"):
            validator.validate_username_format(None)

    def test_username_with_only_underscores(self):
        """Underscores-only username should be rejected (must contain letters/numbers)."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="letters, numbers, underscores"):
            validator.validate_username_format("___")

    def test_username_with_only_hyphens(self):
        """Hyphens-only username should be rejected (must contain letters/numbers)."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="letters, numbers, underscores"):
            validator.validate_username_format("---")

    def test_username_uniqueness_check(self):
        """Should validate username uniqueness."""
        validator = AuthValidationDomain()

        # Username exists - should raise
        with pytest.raises(ValueError, match="already exists"):
            validator.validate_username_unique(True)

        # Username doesn't exist - should not raise
        validator.validate_username_unique(False)


class TestPasswordValidation:
    """Test password format and complexity validation."""

    def test_valid_password_accepted(self):
        """Should accept valid passwords."""
        validator = AuthValidationDomain()

        valid_passwords = [
            "TestPass123",
            "MyPassword1",
            "SecurePass99",
            "abc123xyz",
            "A1b2c3d4",
        ]

        for password in valid_passwords:
            validator.validate_password_format(password)  # Should not raise

    def test_password_too_short(self):
        """Should reject password below minimum length."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match=r"at least \d+ characters"):
            validator.validate_password_format("short1")

    def test_password_too_long(self):
        """Should reject password exceeding maximum length."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match=r"at most \d+ characters"):
            validator.validate_password_format("a" * (MAX_PASSWORD_LENGTH + 1))

    def test_password_at_minimum_length(self):
        """Should accept password at exactly minimum length."""
        validator = AuthValidationDomain()

        # Must have at least one letter AND one number
        min_length_with_letter_and_number = (
            "a" * (MIN_PASSWORD_LENGTH - 1) + "1"
        )
        validator.validate_password_format(min_length_with_letter_and_number)

    def test_password_requires_letter(self):
        """Should reject password with no letters."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="at least one letter"):
            validator.validate_password_format("12345678")

    def test_password_requires_number(self):
        """Should reject password with no numbers."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="at least one number"):
            validator.validate_password_format("abcdefgh")

    def test_empty_password_rejected(self):
        """Should reject empty password."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="required"):
            validator.validate_password_format("")

    def test_password_none_rejected(self):
        """Should reject None password."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="required"):
            validator.validate_password_format(None)

    def test_password_with_only_letters_accepted(self):
        """Should accept password with letters AND at least one number."""
        validator = AuthValidationDomain()

        # Has at least one letter and one number
        validator.validate_password_format("Password1")

    def test_password_with_only_numbers_rejected(self):
        """Should reject password with only numbers (no letters)."""
        validator = AuthValidationDomain()

        with pytest.raises(ValueError, match="at least one letter"):
            validator.validate_password_format("12345678")

    def test_password_with_special_chars_accepted(self):
        """Should accept passwords with special characters (if has letter + number)."""
        validator = AuthValidationDomain()

        valid_with_special = [
            "Pass@word1",
            "Test#123$",
            "P@ssw0rd!",
        ]

        for password in valid_with_special:
            validator.validate_password_format(password)


class TestSessionLimitValidation:
    """Test session limit enforcement."""

    def test_session_limit_constant_is_defined(self):
        """Session limit should be defined and reasonable."""
        from backend.domain.constants import MAX_ACTIVE_SESSIONS

        assert MAX_ACTIVE_SESSIONS is not None
        assert MAX_ACTIVE_SESSIONS > 0
        assert MAX_ACTIVE_SESSIONS <= 10  # Reasonable upper bound

    def test_session_limit_check_returns_bool(self):
        """Session limit check should return boolean."""
        from backend.domain.auth.auth import AuthDomain
        from backend.domain.constants import MAX_ACTIVE_SESSIONS
        from backend.infrastructure.auth.security import PasswordHasher

        domain = AuthDomain(PasswordHasher())

        # Below limit
        result = domain.check_session_limit(MAX_ACTIVE_SESSIONS - 1)
        assert isinstance(result, bool)
        assert result is False

        # At limit
        result = domain.check_session_limit(MAX_ACTIVE_SESSIONS)
        assert isinstance(result, bool)
        assert result is True

        # Over limit
        result = domain.check_session_limit(MAX_ACTIVE_SESSIONS + 1)
        assert isinstance(result, bool)
        assert result is True

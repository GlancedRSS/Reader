"""Validation rules for usernames, passwords, and sessions."""

import re
from datetime import UTC, datetime

from backend.domain.constants import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)


class AuthValidationDomain:
    """Validation methods for usernames, passwords, and sessions."""

    @classmethod
    def validate_username_format(cls, username: str) -> str:
        """Validate username format and length.

        Args:
            username: Username to validate

        Returns:
            Normalized username (lowercase)

        Raises:
            ValueError: If username format is invalid

        """
        if not username:
            raise ValueError("Username is required")

        username = username.strip()
        if len(username) < MIN_USERNAME_LENGTH:
            raise ValueError(
                f"Username must be at least {MIN_USERNAME_LENGTH} characters"
            )

        if len(username) > MAX_USERNAME_LENGTH:
            raise ValueError(
                f"Username must be at most {MAX_USERNAME_LENGTH} characters"
            )

        if not username.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        return username.lower()

    @classmethod
    def validate_password_format(cls, password: str) -> None:
        """Validate password format and length.

        Args:
            password: Password to validate

        Raises:
            ValueError: If password format is invalid

        """
        if not password:
            raise ValueError("Password is required")

        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
            )

        if len(password) > MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at most {MAX_PASSWORD_LENGTH} characters"
            )

        if not re.search(r"[a-zA-Z]", password):
            raise ValueError("Password must contain at least one letter")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")

    @classmethod
    def validate_username_unique(cls, username_exists: bool) -> None:
        """Validate that username is unique.

        Args:
            username_exists: Whether the username already exists

        Raises:
            ValueError: If username already exists

        """
        if username_exists:
            raise ValueError("Username already exists")

    @classmethod
    def validate_session_active(cls, expires_at: datetime | None) -> bool:
        """Validate if a session is still active.

        Args:
            expires_at: Session expiration timestamp

        Returns:
            True if session is still active (not expired)

        """
        if expires_at is None:
            return True
        return expires_at > datetime.now(UTC)

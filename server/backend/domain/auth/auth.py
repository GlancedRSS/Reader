"""Business rules for user authentication, sessions, and password changes."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog

from backend.domain.auth.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
)
from backend.domain.constants import MAX_ACTIVE_SESSIONS

if TYPE_CHECKING:
    from backend.infrastructure.auth.security import PasswordHasher
    from backend.models import User

logger = structlog.get_logger()


class AuthDomain:
    """Business rules for authentication, credentials, and sessions."""

    FIRST_USER_IS_ADMIN = True

    def __init__(self, password_hasher: "PasswordHasher") -> None:
        """Initialize AuthDomain with a password hasher.

        Args:
            password_hasher: PasswordHasher instance with verify_password
                and hash_password methods.

        """
        self.password_hasher = password_hasher

    def update_last_login(self, user: "User") -> None:
        """Update user's last login timestamp (in-memory only).

        The application layer is responsible for persisting this change.

        Args:
            user: User model to update

        """
        user.last_login = datetime.now(UTC)

    def verify_credentials(self, user: "User", password: str) -> None:
        """Verify user credentials.

        Args:
            user: User model with password_hash
            password: Plain text password to verify

        Raises:
            InvalidCredentialsError: If password doesn't match

        """
        if not user.password_hash:
            raise InvalidCredentialsError()

        if not self.password_hasher.verify_password(
            password, user.password_hash
        ):
            raise InvalidCredentialsError()

    def change_user_password(
        self, user: "User", current_password: str, new_password: str
    ) -> None:
        """Change user password after verifying current password.

        This method updates the user model in-memory only.
        The application layer is responsible for persisting the change.

        Args:
            user: User model to update
            current_password: Current password for verification
            new_password: New password to set

        Raises:
            InvalidPasswordError: If current password is invalid

        """
        if not self.password_hasher.verify_password(
            current_password, user.password_hash
        ):
            raise InvalidPasswordError()

        user.password_hash = self.password_hasher.hash_password(new_password)

    def check_session_limit(self, active_session_count: int) -> bool:
        """Check if session limit has been exceeded.

        Args:
            active_session_count: Current number of active sessions

        Returns:
            True if limit exceeded (oldest session should be revoked)

        """
        return active_session_count >= MAX_ACTIVE_SESSIONS

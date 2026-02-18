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
        self.password_hasher = password_hasher

    def update_last_login(self, user: "User") -> None:
        """Update user's last login timestamp (in-memory only; application layer persists)."""
        user.last_login = datetime.now(UTC)

    def verify_credentials(self, user: "User", password: str) -> None:
        """Verify user credentials."""
        if not user.password_hash:
            raise InvalidCredentialsError()

        if not self.password_hasher.verify_password(
            password, user.password_hash
        ):
            raise InvalidCredentialsError()

    def change_user_password(
        self, user: "User", current_password: str, new_password: str
    ) -> None:
        """Change user password after verifying current password (in-memory only; application layer persists)."""
        if not self.password_hasher.verify_password(
            current_password, user.password_hash
        ):
            raise InvalidPasswordError()

        user.password_hash = self.password_hasher.hash_password(new_password)

    def check_session_limit(self, active_session_count: int) -> bool:
        """Check if session limit exceeded (returns True if oldest session should be revoked)."""
        return active_session_count >= MAX_ACTIVE_SESSIONS

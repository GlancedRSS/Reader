"""Password hashing and token generation utilities."""

import hashlib
import secrets

from passlib.context import CryptContext

from backend.core.app import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


class PasswordHasher:
    """Password hashing using passlib with pbkdf2_sha256."""

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """Verify a password against its hash."""
        return bool(pwd_context.verify(plain_password, hashed_password))

    def hash_password(self, password: str) -> str:
        """Generate password hash."""
        result = pwd_context.hash(password)
        return str(result)


def hash_token(token: str) -> str:
    """Hash a token for secure storage using SHA256."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_urlsafe(settings.csrf_token_length)

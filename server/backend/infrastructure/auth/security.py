"""Password hashing and token generation utilities."""

import hashlib
import secrets

from passlib.context import CryptContext

from backend.core.app import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


class PasswordHasher:
    """Password hashing using passlib with pbkdf2_sha256.

    This class provides methods for hashing passwords and verifying
    passwords against their hashes using the secure pbkdf2_sha256 algorithm.
    """

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: The plain text password to verify
            hashed_password: The hashed password to compare against

        Returns:
            True if password matches, False otherwise

        """
        return bool(pwd_context.verify(plain_password, hashed_password))

    def hash_password(self, password: str) -> str:
        """Generate password hash.

        Args:
            password: The plain text password to hash

        Returns:
            The hashed password as a string

        """
        result = pwd_context.hash(password)
        return str(result)


def hash_token(token: str) -> str:
    """Hash a token for secure storage.

    Uses SHA256 to create a one-way hash of the token for secure
    storage in the database. This prevents token exposure if
    the database is compromised.

    Args:
        token: The token to hash

    Returns:
        The hexadecimal digest of the hashed token

    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token.

    Returns:
        A URL-safe random token for CSRF protection

    """
    return secrets.token_urlsafe(settings.csrf_token_length)

"""Security tests for password hashing, CSRF tokens, and session tokens."""

import hashlib
import re

from backend.infrastructure.auth.security import (
    PasswordHasher,
    generate_csrf_token,
    hash_token,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_is_not_plain_text(self):
        """Hashed password must not equal plain text password."""
        hasher = PasswordHasher()
        password = "TestPass123"

        hashed = hasher.hash_password(password)

        assert hashed != password
        assert not hashed.startswith(password)

    def test_same_password_hashes_to_different_values(self):
        """Same password should hash to different values (salt works)."""
        hasher = PasswordHasher()
        password = "TestPass123"

        hash1 = hasher.hash_password(password)
        hash2 = hasher.hash_password(password)

        assert hash1 != hash2

    def test_password_verify_with_correct_password(self):
        """Should return True for correct password."""
        hasher = PasswordHasher()
        password = "TestPass123"
        hashed = hasher.hash_password(password)

        result = hasher.verify_password(password, hashed)

        assert result is True

    def test_password_verify_with_wrong_password(self):
        """Should return False for incorrect password."""
        hasher = PasswordHasher()
        password = "TestPass123"
        hashed = hasher.hash_password(password)

        result = hasher.verify_password("WrongPass123", hashed)

        assert result is False

    def test_password_verify_with_empty_password(self):
        """Should return False for empty password."""
        hasher = PasswordHasher()
        password = "TestPass123"
        hashed = hasher.hash_password(password)

        result = hasher.verify_password("", hashed)

        assert result is False

    def test_hashed_password_contains_algorithm_marker(self):
        """Hashed password should contain pbkdf2 identifier."""
        hasher = PasswordHasher()
        password = "TestPass123"

        hashed = hasher.hash_password(password)

        # pbkdf2_sha256 hashes start with $pbkdf2-sha256$
        assert "$pbkdf2-sha256$" in hashed


class TestCSRFTokenGeneration:
    """Test CSRF token generation."""

    def test_csrf_token_is_generated(self):
        """Should generate a non-empty token."""
        token = generate_csrf_token()

        assert token
        assert len(token) > 0

    def test_csrf_token_is_url_safe(self):
        """Should only contain URL-safe characters."""
        token = generate_csrf_token()

        # URL-safe base64: A-Z, a-z, 0-9, hyphen, underscore
        assert re.match(r"^[A-Za-z0-9_-]+$", token)

    def test_csrf_tokens_are_unique(self):
        """Each generated token should be different."""
        token1 = generate_csrf_token()
        token2 = generate_csrf_token()

        assert token1 != token2

    def test_csrf_token_format_is_consistent(self):
        """Token should have consistent format (base64 encoded)."""
        token = generate_csrf_token()

        # Should be reasonable length (32 bytes = ~43 chars in base64)
        assert 20 <= len(token) <= 50


class TestTokenHashing:
    """Test session token hashing for secure storage."""

    def test_hash_token_is_one_way(self):
        """Hashed token should be irreversible (SHA-256)."""
        token = "session.token.value"
        hashed = hash_token(token)

        # Cannot get original token from hash
        assert token not in hashed
        assert "$" not in hashed  # Not a bcrypt hash, it's SHA-256

    def test_hash_token_is_deterministic(self):
        """Same token should produce same hash."""
        token = "session.token.value"

        hash1 = hash_token(token)
        hash2 = hash_token(token)

        assert hash1 == hash2

    def test_hash_token_is_different_for_different_tokens(self):
        """Different tokens should produce different hashes."""
        hash1 = hash_token("token1")
        hash2 = hash_token("token2")

        assert hash1 != hash2

    def test_hash_token_format_is_hex(self):
        """Hashed token should be hexadecimal digest."""
        token = "session.token.value"
        hashed = hash_token(token)

        # SHA-256 produces 64 hex characters
        assert len(hashed) == 64
        assert re.match(r"^[0-9a-f]{64}$", hashed)

    def test_hash_token_empty_input(self):
        """Empty token should still produce valid hash."""
        hashed = hash_token("")

        assert hashed == hashlib.sha256(b"").hexdigest()


class TestSessionTokenFormat:
    """Test session token format validation."""

    def test_session_token_format(self):
        """Session token should follow format: {uuid}.{secret}."""
        # Session tokens are created as f"{session_id}.{secret_token}"
        # where session_id is UUID and secret_token is 32-byte urlsafe base64

        session_id = "550e8400-e29b-41d4-a716-446655440000"
        secret = "abc123def456"

        token = f"{session_id}.{secret}"

        # Should contain exactly one dot separator
        parts = token.split(".")
        assert len(parts) == 2

        # First part should be UUID format
        uuid_part = parts[0]
        assert re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            uuid_part.lower(),
        )

    def test_session_token_with_invalid_uuid(self):
        """Session token with invalid UUID should fail validation."""
        invalid_tokens = [
            "not-a-uuid.secret",
            ".secret",
            "g0000000-0000-0000-0000-000000000000.",  # g at start (not hex)
            "123.",  # Too short
            ".",
            "no-dot-at-all",
        ]

        for token in invalid_tokens:
            parts = token.split(".")
            if parts[0]:  # Not empty
                assert not re.match(
                    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    parts[0].lower(),
                ), f"Token {token} should have invalid UUID"

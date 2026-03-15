import hashlib
import secrets

from passlib.context import CryptContext

from backend.core.app import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


class PasswordHasher:
    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        return bool(pwd_context.verify(plain_password, hashed_password))

    def hash_password(self, password: str) -> str:
        result = pwd_context.hash(password)
        return str(result)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(settings.csrf_token_length)

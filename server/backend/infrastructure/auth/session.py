"""Cookie management for session and CSRF tokens."""

from datetime import UTC, datetime, timedelta
from typing import Any

from backend.core.app import settings


class CookieManager:
    """Manages session and CSRF cookie generation and clearing."""

    def generate_session_cookies(
        self, session_token: str, csrf_token: str
    ) -> dict[str, Any]:
        """Generate cookie settings for session and CSRF tokens."""
        expiration = datetime.now(UTC) + timedelta(
            seconds=settings.session_cookie_max_age
        )

        session_cookie = {
            "key": settings.session_cookie_name,
            "value": session_token,
            "max_age": settings.session_cookie_max_age,
            "expires": expiration,
            "path": "/",
            "domain": None,
            "secure": settings.session_cookie_secure_effective,
            "httponly": settings.session_cookie_httponly,
            "samesite": settings.session_cookie_samesite,
        }

        csrf_cookie = {
            "key": settings.csrf_cookie_name,
            "value": csrf_token,
            "max_age": settings.session_cookie_max_age,
            "expires": expiration,
            "path": "/",
            "domain": None,
            "secure": settings.session_cookie_secure_effective,
            "httponly": False,
            "samesite": settings.session_cookie_samesite,
        }

        return {
            "session_cookie": session_cookie,
            "csrf_cookie": csrf_cookie,
            "csrf_token": csrf_token,
        }

    def generate_clear_cookies(self) -> dict[str, Any]:
        """Generate cookie settings to clear session and CSRF cookies."""
        session_cookie = {
            "key": settings.session_cookie_name,
            "path": "/",
            "domain": None,
            "secure": settings.session_cookie_secure_effective,
            "httponly": settings.session_cookie_httponly,
            "samesite": settings.session_cookie_samesite,
        }

        csrf_cookie = {
            "key": settings.csrf_cookie_name,
            "path": "/",
            "domain": None,
            "secure": settings.session_cookie_secure_effective,
            "httponly": False,
            "samesite": settings.session_cookie_samesite,
        }

        return {
            "session_cookie": session_cookie,
            "csrf_cookie": csrf_cookie,
        }

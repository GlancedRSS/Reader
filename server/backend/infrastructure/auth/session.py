from datetime import UTC, datetime, timedelta
from typing import Any

from backend.core.app import settings


class CookieManager:
    def generate_session_cookies(
        self, session_token: str, csrf_token: str
    ) -> dict[str, Any]:
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

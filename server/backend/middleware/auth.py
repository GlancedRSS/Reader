"""Authentication middleware for httpOnly cookie-based session verification."""

import re
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING
from urllib.parse import unquote

import structlog
from fastapi import FastAPI, HTTPException, Request, Response, status
from sqlalchemy import text
from starlette.responses import JSONResponse

from backend.core.app import settings
from backend.core.database import get_db
from backend.infrastructure.repositories.session import (
    get_current_user_from_cookie,
)

if TYPE_CHECKING:
    pass

logger = structlog.get_logger()

CSRF_PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


def _normalize_path(path: str) -> str:
    """Normalize URL path to prevent authentication bypass attempts."""
    normalized = unquote(path)
    normalized = re.sub(r"/+", "/", normalized)
    if normalized != "/" and normalized.endswith("/"):
        normalized = normalized.rstrip("/")
    return normalized


def _verify_csrf_token(request: Request) -> None:
    """Verify CSRF token from header matches cookie value."""
    csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
    csrf_header = request.headers.get("X-CSRF-Token")

    if not csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF cookie missing",
        )

    if not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required in header",
        )

    if csrf_header != csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )


def _is_public_endpoint(normalized_path: str, request_method: str) -> bool:
    """Check if the endpoint is public and doesn't require authentication."""
    public_paths = {
        "/health",
        "/health/detailed",
        "/health/metrics",
        "/health/system",
        "/",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/sse/notifications",
        "/redoc",
    }

    dev_paths = {
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    dev_path_prefixes: set[str] = set()

    return (
        normalized_path in public_paths
        or request_method == "OPTIONS"
        or (
            settings.environment == "development"
            and (
                normalized_path in dev_paths
                or any(normalized_path.startswith(p) for p in dev_path_prefixes)
            )
        )
    )


def add_auth_middleware(app: "FastAPI") -> None:
    """Add authentication middleware to FastAPI app."""

    @app.middleware("http")
    async def authentication_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Verify httpOnly cookie session and set user context."""
        normalized_path = _normalize_path(request.url.path)

        if _is_public_endpoint(normalized_path, request.method):
            return await call_next(request)

        try:
            if (
                normalized_path.startswith("/api/v1/")
                and request.method != "OPTIONS"
            ):
                await _verify_session_cookie(request)

                if request.method in CSRF_PROTECTED_METHODS:
                    _verify_csrf_token(request)

            return await call_next(request)

        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "status_code": e.status_code},
            )


async def _verify_session_cookie(request: Request) -> None:
    """Verify httpOnly cookie session and extract user ID."""
    start_time = time.time()

    session_token = request.cookies.get(settings.session_cookie_name)

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    lookup_start = time.time()
    try:
        async for db in get_db():
            user = await get_current_user_from_cookie(session_token, db)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session",
                )

            request.state.user_id = user.id

            await db.execute(
                text("SELECT public.set_app_context(:user_id)"),
                {"user_id": str(user.id)},
            )

            lookup_elapsed = time.time() - lookup_start
            total_elapsed = time.time() - start_time

            # Only log if auth takes more than 100ms
            if total_elapsed > 0.1:
                logger.info(
                    "Session verification complete",
                    lookup_elapsed_ms=round(lookup_elapsed * 1000, 2),
                    total_elapsed_ms=round(total_elapsed * 1000, 2),
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Database error during user lookup",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during authentication",
        ) from e

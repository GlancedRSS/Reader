"""FastAPI application entry point and configuration."""

import asyncio
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .core import active_requests, setup_logging, shutdown_event
from .core.app import settings
from .core.exceptions import (
    AccessDeniedError,
    ApplicationException,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from .core.lifecycle import lifespan_init, lifespan_shutdown
from .middleware.auth import add_auth_middleware
from .routers import (
    article,
    auth,
    discovery,
    feed,
    folder,
    notification,
    opml,
    search,
    tag,
    user,
)
from .schemas.core import ErrorResponse

setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle."""
    await lifespan_init()
    yield
    await lifespan_shutdown()


def _remove_422_from_openapi(openapi_schema: dict[str, Any]) -> dict[str, Any]:
    """Remove 422 validation error responses from OpenAPI schema."""
    if "paths" in openapi_schema:
        for _, method_item in openapi_schema["paths"].items():
            for _, param in method_item.items():
                responses = param.get("responses")
                if responses and "422" in responses:
                    del responses["422"]
    return openapi_schema


_openapi = FastAPI.openapi


def openapi(self: FastAPI) -> dict[str, Any]:
    """Generate OpenAPI schema with 422 errors removed."""
    original_schema = _openapi(self)
    return _remove_422_from_openapi(original_schema)


FastAPI.openapi = openapi

app = FastAPI(
    title="Glanced Reader API",
    description="API for Glanced Reader",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

add_auth_middleware(app)


@app.get("/health")
@app.head("/health")
async def health() -> JSONResponse:
    """Health check endpoint for docker healthcheck and load balancers."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "version": settings.version},
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next: Any) -> Any:
    """Add a unique X-Request-ID header to responses for tracing."""
    request_id = uuid.uuid4()
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = str(request_id)
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Any) -> Any:
    """Add security headers to responses."""
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "origin-when-cross-origin"

    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    if settings.environment == "development":
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https: https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
    else:
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

    response.headers["Content-Security-Policy"] = csp

    return response


@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    """Log incoming requests with timing and status codes."""
    start_time = time.time()
    request_id = getattr(request.state, "request_id", None)

    if shutdown_event.is_set():
        logger.info(
            "Rejecting request during shutdown",
            method=request.method,
            url=str(request.url),
            request_id=request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                error="SERVICE_UNAVAILABLE",
                message="Server is shutting down",
                details={"retry_after": 30},
                timestamp=datetime.now(UTC),
                request_id=request_id,
            ).model_dump(mode="json"),
            headers={"Retry-After": "30"},
        )

    request_task = asyncio.current_task()
    if request_task:
        active_requests.add(request_task)

    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request_id,
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
            request_id=request_id,
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response
    finally:
        if request_task:
            active_requests.discard(request_task)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        url=str(request.url),
        request_id=getattr(request.state, "request_id", None),
    )

    error_type = "VALIDATION_ERROR" if exc.status_code == 422 else "HTTP_ERROR"

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=error_type,
            message=exc.detail,
            details={"status_code": exc.status_code},
            timestamp=datetime.now(UTC),
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(mode="json"),
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        url=str(request.url),
        request_id=getattr(request.state, "request_id", None),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details=(
                {"error_type": type(exc).__name__}
                if settings.environment == "development"
                else None
            ),
            timestamp=datetime.now(UTC),
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(mode="json"),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with user-friendly messages."""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        url=str(request.url),
        request_id=getattr(request.state, "request_id", None),
    )

    error_messages = []

    for error in exc.errors():
        field_name = error["loc"][-1] if error["loc"] else "field"
        field_name_str = str(field_name)

        if field_name_str.lower() == "password":
            error_type = error["type"]
            if error_type == "string_too_short":
                min_length = error["ctx"].get("min_length", 8)
                error_messages.append(
                    f"Password must be at least {min_length} characters long"
                )
            elif error_type == "string_pattern_mismatch":
                error_msg = error.get("msg", "").lower()
                if "letter" in error_msg:
                    error_messages.append(
                        "Password must contain at least one letter"
                    )
                elif "number" in error_msg or "digit" in error_msg:
                    error_messages.append(
                        "Password must contain at least one number"
                    )
                else:
                    error_messages.append("Password format is invalid")
            else:
                error_messages.append("Password is invalid")
            continue

        FIELD_NAME_MAPPING = {
            "username": "Username",
            "current_password": "Current password",
            "new_password": "New password",
            "limit": "Limit",
            "offset": "Offset",
            "title": "Title",
            "url": "URL",
            "description": "Description",
            "session_id": "Session ID",
            "feed_id": "Feed ID",
            "folder_id": "Folder ID",
            "article_id": "Article ID",
            "tag_id": "Tag ID",
        }

        user_friendly_field = FIELD_NAME_MAPPING.get(
            field_name_str.lower(), field_name_str.replace("_", " ").title()
        )

        error_type = error["type"]
        if error_type == "missing":
            error_messages.append(f"{user_friendly_field} is required")
        elif error_type == "string_too_short":
            min_length = error["ctx"].get("min_length")
            if min_length is not None:
                error_messages.append(
                    f"{user_friendly_field} must be at least {min_length} characters long"
                )
            else:
                error_messages.append(f"{user_friendly_field} is too short")
        elif error_type == "string_too_long":
            max_length = error["ctx"].get("max_length")
            if max_length is not None:
                error_messages.append(
                    f"{user_friendly_field} must be no more than {max_length} characters long"
                )
            else:
                error_messages.append(f"{user_friendly_field} is too long")
        elif error_type == "string_pattern_mismatch":
            error_messages.append(
                f"{user_friendly_field} contains invalid characters"
            )
        elif error_type == "value_error.number.not_ge":
            min_value = error["ctx"].get("ge_value")
            if min_value is not None:
                error_messages.append(
                    f"{user_friendly_field} must be at least {min_value}"
                )
            else:
                error_messages.append(f"{user_friendly_field} is too small")
        elif error_type == "value_error.number.not_le":
            max_value = error["ctx"].get("le_value")
            if max_value is not None:
                error_messages.append(
                    f"{user_friendly_field} must be no more than {max_value}"
                )
            else:
                error_messages.append(f"{user_friendly_field} is too large")
        elif error_type == "bool_parsing":
            error_messages.append(
                f"{user_friendly_field} must be true or false"
            )
        elif field_name_str.lower() in ["url", "website"]:
            error_messages.append("URL is not valid")
        elif "uuid" in field_name_str.lower():
            error_messages.append(
                f"{user_friendly_field} is not a valid ID format"
            )
        else:
            error_messages.append(error.get("msg", "Validation error"))

    user_message = (
        "; ".join(error_messages)
        if len(error_messages) > 1
        else error_messages[0]
        if error_messages
        else "Validation failed"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message=user_message,
            details={
                "validation_errors": (
                    exc.errors()
                    if settings.environment == "development"
                    else None
                ),
                "status_code": 422,
            },
            timestamp=datetime.now(UTC),
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(mode="json"),
    )


@app.exception_handler(ApplicationException)
async def application_exception_handler(
    request: Request, exc: ApplicationException
) -> JSONResponse:
    """Handle domain-specific application exceptions."""
    status_codes = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        AccessDeniedError: status.HTTP_403_FORBIDDEN,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
    }

    status_code = status_codes.get(
        type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    logger.warning(
        "Application exception",
        exception_type=type(exc).__name__,
        message=exc.message,
        status_code=status_code,
        url=str(request.url),
        request_id=getattr(request.state, "request_id", None),
    )

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=type(exc).__name__.upper(),
            message=exc.message,
            details={"status_code": status_code},
            timestamp=datetime.now(UTC),
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(mode="json"),
    )


app.include_router(article.router, prefix="/api/v1/articles", tags=["Articles"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(feed.router, prefix="/api/v1/feeds", tags=["Feeds"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(folder.router, prefix="/api/v1/folders", tags=["Folders"])
app.include_router(tag.router, prefix="/api/v1/tags", tags=["Tags"])
app.include_router(
    discovery.router, prefix="/api/v1/discovery", tags=["Discovery"]
)
app.include_router(opml.router, prefix="/api/v1/opml", tags=["OPML"])
app.include_router(user.router, prefix="/api/v1/me", tags=["User"])
app.include_router(
    notification.router, prefix="/api/v1/notifications", tags=["Notifications"]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level,
    )

"""Application configuration with environment variable support."""

import os
import tomllib
from pathlib import Path

import structlog
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment files in precedence order (later files override earlier ones)
# 1. .env.example (base defaults)
# 2. .env.development or .env.production (environment-specific)
# 3. .env.local (your local overrides)
_base_dir = Path(__file__).parent.parent.parent
load_dotenv(_base_dir / ".env.example", override=False)

_env = os.getenv("ENVIRONMENT", "development").lower()
load_dotenv(_base_dir / f".env.{_env}", override=True)

load_dotenv(_base_dir / ".env.local", override=True)


def _get_version() -> str:
    """Read version from pyproject.toml.

    Returns:
        Version string from pyproject.toml, or fallback default.

    """
    try:
        pyproject_path = _base_dir / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception:
        return "0.0.0"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: PostgreSQL connection URL.
        environment: Application environment (development or production).
        version: API version string.
        host: Host address to bind the server to.
        port: Port number for the server.
        api_base_url: Base URL for API (used for internal callbacks).
        user_agent: User agent string for feed requests.
        request_timeout: Request timeout in seconds.
        max_concurrent_feeds: Maximum concurrent feed processing.
        feed_refresh_interval_minutes: Minutes between feed refreshes.
        feed_refresh_batch_size: Number of concurrent feed refreshes (flow control).
        max_feed_size_mb: Maximum feed size in megabytes.
        log_level: Logging level (debug, info, warning, error, critical).
        log_format: Log format (text or json).
        redis_url: Redis connection URL.
        redis_max_connections: Maximum Redis connections.

    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/reader",
        description="PostgreSQL connection URL",
    )

    environment: str = Field(default="production")

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode.

        Returns:
            True if environment is development, False otherwise.

        """
        return self.environment.lower() == "development"

    version: str = Field(
        default_factory=_get_version,
        description="Application version (read from pyproject.toml)",
    )
    host: str = "0.0.0.0"
    port: int = 2076
    api_base_url: str = Field(
        default="http://localhost:2076",
        description="Base URL for API (used for internal callbacks)",
    )

    @property
    def user_agent(self) -> str:
        """Get user agent string for feed requests.

        Returns:
            User agent string with current version.
        """
        return f"Glanced-Reader/{self.version} (+https://github.com/glancedrss/reader)"

    request_timeout: int = 30
    max_concurrent_feeds: int = Field(default=50)
    feed_refresh_interval_minutes: int = Field(default=30)
    feed_refresh_batch_size: int = Field(default=10)
    max_feed_size_mb: int = Field(default=5)
    log_level: str = Field(default="info")
    log_format: str = Field(default="json")

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL. Uses redis-py async client.",
    )
    redis_max_connections: int = Field(
        default=50,
        description="Maximum number of Redis connections",
    )
    redis_keyspace_db: int = Field(
        default=0,
        description="Redis database number for keyspace notifications (must match Redis URL DB)",
    )

    session_timeout_days: int = Field(
        default=30,
        description="Session cookie lifetime in days",
    )
    session_cookie_name: str = "session_id"
    session_cookie_secure: bool = Field(
        default=True,
        description="Set Secure flag on session cookies (HTTPS only in production)",
    )
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    csrf_cookie_name: str = "csrf_token"
    csrf_token_length: int = 32
    cookie_secure: bool | None = Field(
        default=None,
        description="Override cookie secure flag. Set via COOKIE_SECURE env var. If not set, auto-detects based on environment (dev=false, prod=true).",
    )

    @property
    def session_cookie_secure_effective(self) -> bool:
        """Get the effective secure flag for cookies.

        Priority:
        1. COOKIE_SECURE env var (if set)
        2. Development mode (false) or Production mode (true)

        Returns:
            True if cookies should be secure (HTTPS only), False otherwise.

        """
        if self.cookie_secure is not None:
            return self.cookie_secure
        if self.is_development:
            return False
        return self.session_cookie_secure

    @property
    def session_cookie_max_age(self) -> int:
        """Get the session cookie max age in seconds.

        Returns:
            Session lifetime in seconds.

        """
        return self.session_timeout_days * 24 * 60 * 60

    storage_path: str = Field(
        default="../data",
        description="Path to local storage directory for OPML files",
    )

    opml_max_file_size: int = Field(
        default=16 * 1024 * 1024,
        description="Maximum OPML file size in bytes",
    )
    opml_max_folder_depth: int = Field(
        default=9,
        description="Maximum folder depth before flattening",
    )
    opml_import_timeout_seconds: int = Field(
        default=300,
        description="Maximum time to process OPML import",
    )

    @property
    def storage_config(self) -> dict[str, str]:
        """Get storage configuration as a dictionary.

        Returns:
            Dictionary with storage configuration.

        """
        return {
            "path": self.storage_path,
        }


def validate_configuration() -> tuple[bool, list[str]]:
    """Validate all required configuration and provide helpful error messages.

    Returns:
        A tuple of (is_valid, list_of_error_messages).

    """
    logger = structlog.get_logger()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        logger.info("Validating database configuration...")
        test_db_url = settings.database_url

        if "postgresql" not in test_db_url:
            errors.append(
                "DATABASE_URL must be a valid PostgreSQL connection string"
            )

        logger.info("Validating Redis configuration...")
        if not settings.redis_url:
            errors.append("REDIS_URL must be set")

        logger.info("Validating Session configuration...")
        if settings.session_cookie_max_age <= 0:
            errors.append("SESSION_COOKIE_MAX_AGE must be positive")

        if settings.csrf_token_length < 16:
            warnings.append(
                "CSRF_TOKEN_LENGTH should be at least 16 for security"
            )

        logger.info("Validating performance configuration...")
        if settings.max_concurrent_feeds <= 0:
            errors.append("MAX_CONCURRENT_FEEDS must be positive")

        if settings.max_concurrent_feeds > 100:
            warnings.append(
                "MAX_CONCURRENT_FEEDS over 100 may overwhelm the system"
            )

        if settings.request_timeout <= 0:
            errors.append("REQUEST_TIMEOUT must be positive")

        logger.info("Validating logging configuration...")
        valid_log_levels = ["debug", "info", "warning", "error", "critical"]
        if settings.log_level.lower() not in valid_log_levels:
            errors.append(
                f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}"
            )

        for warning in warnings:
            logger.warning("Configuration warning", warning=warning)

        success = len(errors) == 0
        if success:
            logger.info("Configuration validation passed")
        else:
            logger.error(
                "Configuration validation failed", error_count=len(errors)
            )

        return success, errors

    except Exception as e:
        logger.exception(
            "Configuration validation failed with exception", error=str(e)
        )
        errors.append(f"Configuration validation failed: {e!s}")
        return False, errors


def get_configuration_help() -> dict[str, str]:
    """Get help information for common configuration issues.

    Returns:
        A dictionary mapping configuration variables to help text.

    """
    return {
        "DATABASE_URL": """
            PostgreSQL connection URL.
            Format: postgresql://user:password@host/database
            Example: export DATABASE_URL="postgresql://user:pass@localhost:5432/reader"
        """,
        "REDIS_URL": """
            Redis URL for caching, pubsub, and SSE notifications.
            Example: export REDIS_URL="redis://localhost:6379/0"
        """,
        "SESSION_TIMEOUT_DAYS": """
            Session timeout in days (default: 30).
            Example: export SESSION_TIMEOUT_DAYS="30"
        """,
        "COOKIE_SECURE": """
            Override cookie secure flag for HTTP vs HTTPS.
            - Set to "true" for HTTPS/production exposed to internet
            - Set to "false" for HTTP/LAN usage
            - If not set, auto-detects: dev=false, prod=true
            Example: export COOKIE_SECURE="false"
        """,
        "ENVIRONMENT": """
            Application environment (development or production).
            Affects logging levels and error reporting.
            Example: export ENVIRONMENT="production"
        """,
        "LOG_LEVEL": """
            Logging verbosity level.
            Valid values: debug, info, warning, error, critical.
            Production should use 'info' or higher.
        """,
        "MAX_CONCURRENT_FEEDS": """
            Maximum number of feeds to process simultaneously.
            Recommended: 5-10 for most deployments, up to 50 for powerful servers.
        """,
    }


settings = Settings()

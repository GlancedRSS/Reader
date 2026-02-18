"""HTTP client service for centralized HTTP operations."""

from importlib.metadata import version as get_version
from typing import Any

import httpx

from backend.core.app import settings

_VERSION = get_version("glanced-reader-server")


class HttpClient:
    """Configuration provider for secure HTTP client."""

    @staticmethod
    def get_secure_client_config() -> dict[str, Any]:
        """Return configuration for secure HTTP client with timeouts, size limits, and headers."""
        return {
            "timeout_config": httpx.Timeout(
                connect=5.0,
                read=15.0,
                write=10.0,
                pool=30.0,
            ),
            "max_response_size": settings.max_feed_size_mb * 1024 * 1024,
            "max_redirects": 3,
            "default_headers": {
                "User-Agent": f"Glanced-Reader/{_VERSION} (+https://github.com/glancedrss/reader)",
                "Accept": "application/rss+xml, application/atom+xml, application/rdf+xml, text/xml, application/xml;q=0.9, text/html;q=0.8, */*;q=0.1",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            },
        }


class SecureHTTPClient:
    """HTTP client with security hardening for resource-constrained environments."""

    def __init__(self) -> None:
        """Initialize the HTTP client with secure configuration."""
        config = HttpClient.get_secure_client_config()
        self.timeout_config = config["timeout_config"]
        self.max_response_size = config["max_response_size"]
        self.max_redirects = config["max_redirects"]
        self.default_headers = config["default_headers"]

    def create_client(self) -> httpx.AsyncClient:
        """Create a secure HTTP client with connection limits and timeouts."""
        limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=30.0,
        )

        return httpx.AsyncClient(
            timeout=self.timeout_config,
            limits=limits,
            headers=self.default_headers,
            follow_redirects=True,
            max_redirects=self.max_redirects,
            verify=True,
        )

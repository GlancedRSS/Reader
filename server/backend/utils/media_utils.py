"""Shared utilities for media extraction and validation."""

from typing import Any
from urllib.parse import urlparse

import structlog

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".svg",
    ".ico",
}

logger = structlog.get_logger()


def validate_logo_url(logo_url: str) -> bool:
    """Validate logo URL for security and format."""
    if not logo_url or not isinstance(logo_url, str):
        return False

    try:
        parsed = urlparse(logo_url)
        if not parsed.scheme or not parsed.netloc:
            return False
    except Exception:
        return False

    path_lower = urlparse(logo_url).path.lower()
    has_image_extension = any(
        path_lower.endswith(ext) for ext in IMAGE_EXTENSIONS
    )

    if has_image_extension or len(path_lower) == 0 or "?" in path_lower:
        return True

    return False


def is_valid_image_url(url: str) -> bool:
    """Check if URL is a valid image URL."""
    if not url or not url.startswith(("http://", "https://")):
        return False

    parsed = urlparse(url.lower())
    if any(parsed.path.endswith(ext) for ext in IMAGE_EXTENSIONS):
        return True

    return False


def detect_feed_type(feed: Any) -> str:
    """Detect feed type (RSS, Atom, RDF) from feedparser feed object."""
    feed_type = "rss"
    if hasattr(feed, "version") and feed.version:
        if "atom" in feed.version.lower():
            feed_type = "atom"
        elif "rdf" in feed.version.lower():
            feed_type = "rdf"
        elif "rss" in feed.version.lower():
            feed_type = "rss"

    return feed_type

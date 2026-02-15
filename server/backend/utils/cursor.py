"""Cursor pagination utilities for encoding/decoding pagination tokens."""

import base64
import json
from datetime import datetime
from typing import Any
from uuid import UUID


def encode_cursor_data(cursor_data: dict[str, Any]) -> str:
    """Encode cursor data to base64 string.

    Args:
        cursor_data: Dictionary with cursor data

    Returns:
        Base64-encoded cursor string

    """
    cursor_json = json.dumps(cursor_data)
    return base64.b64encode(cursor_json.encode("utf-8")).decode("utf-8")


def parse_cursor_data(cursor: str | None) -> dict[str, Any] | None:
    """Parse cursor string into components.

    Args:
        cursor: The base64-encoded JSON cursor string to parse

    Returns:
        Dictionary with cursor data, or None if invalid

    """
    if not cursor:
        return None

    try:
        decoded = base64.b64decode(cursor).decode("utf-8")
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError):
        return None


def create_article_cursor_data(
    article_id: UUID, published_at: datetime | None, created_at: datetime
) -> dict[str, Any]:
    """Create cursor data from article.

    Args:
        article_id: The article ID
        published_at: The article's published timestamp
        created_at: The article's created timestamp (used when published_at is null)

    Returns:
        Dictionary with cursor data

    """
    cursor_value = (
        published_at.isoformat() if published_at else created_at.isoformat()
    )
    return {
        "timestamp": cursor_value,
        "is_published_at": published_at is not None,
        "article_id": str(article_id),
    }


def create_feed_cursor_data(
    user_feed_id: UUID, last_update: datetime | None
) -> dict[str, Any]:
    """Create cursor data from user feed.

    Args:
        user_feed_id: The user feed ID
        last_update: The feed's last update timestamp

    Returns:
        Dictionary with cursor data

    """
    return {
        "last_update": (last_update.isoformat() if last_update else None),
        "user_feed_id": str(user_feed_id),
    }


def create_search_cursor_data(
    article_id: UUID,
    published_at: datetime | None,
    created_at: datetime,
    relevance_score: float,
) -> dict[str, Any]:
    """Create cursor data from search result.

    For search, we sort by relevance score first, then by timestamp.
    The cursor must include the relevance score to maintain ordering.

    Args:
        article_id: The article ID
        published_at: The article's published timestamp
        created_at: The article's created timestamp (used when published_at is null)
        relevance_score: The search relevance score

    Returns:
        Dictionary with cursor data

    """
    cursor_timestamp = (
        published_at.isoformat() if published_at else created_at.isoformat()
    )
    return {
        "relevance": str(relevance_score),
        "timestamp": cursor_timestamp,
        "is_published_at": published_at is not None,
        "article_id": str(article_id),
    }

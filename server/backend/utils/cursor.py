"""Cursor pagination utilities for encoding/decoding pagination tokens."""

import base64
import json
from datetime import datetime
from typing import Any
from uuid import UUID


def encode_cursor_data(cursor_data: dict[str, Any]) -> str:
    """Encode cursor data to base64 string."""
    cursor_json = json.dumps(cursor_data)
    return base64.b64encode(cursor_json.encode("utf-8")).decode("utf-8")


def parse_cursor_data(cursor: str | None) -> dict[str, Any] | None:
    """Parse cursor string into components."""
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
    """Create cursor data from article."""
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
    """Create cursor data from user feed."""
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
    """Create cursor data from search result."""
    cursor_timestamp = (
        published_at.isoformat() if published_at else created_at.isoformat()
    )
    return {
        "relevance": str(relevance_score),
        "timestamp": cursor_timestamp,
        "is_published_at": published_at is not None,
        "article_id": str(article_id),
    }

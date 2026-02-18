"""Date parsing utilities for article and feed processing."""

from datetime import UTC, datetime


def parse_iso_datetime(date_string: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string with timezone support."""
    if not date_string:
        return None

    try:
        if date_string.endswith("Z"):
            date_string = date_string.replace("Z", "+00:00")

        parsed = datetime.fromisoformat(date_string)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        else:
            parsed = parsed.astimezone(UTC)

        return parsed

    except (ValueError, TypeError, AttributeError):
        return None

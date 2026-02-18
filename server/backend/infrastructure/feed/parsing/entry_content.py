"""RSS/ATOM feed entry extraction utilities."""

from datetime import UTC, datetime
from typing import Any

try:
    from feedparser import (
        _parse_date as feedparser_parse_date,
    )
except ImportError:
    feedparser_parse_date = None

import structlog


class EntryExtractor:
    """Extracts structured content from individual RSS/ATOM feed entries."""

    def extract_content_from_entry(
        self, entry: Any
    ) -> tuple[str | None, str | None]:
        """Extract content from dedicated content XML tags only."""
        if hasattr(entry, "media_group") and entry.media_group:
            for group in entry.media_group:
                if isinstance(group, dict):
                    media_description = group.get("media_description")
                    if (
                        media_description
                        and isinstance(media_description, str)
                        and media_description.strip()
                    ):
                        return media_description, "media:description"

        if hasattr(entry, "content") and entry.content:
            if isinstance(entry.content, list):
                for item in entry.content:
                    if isinstance(item, dict):
                        content_value = item.get("value", "")
                        if content_value and content_value.strip():
                            return content_value, "atom:content"
            elif isinstance(entry.content, str) and entry.content.strip():
                return entry.content, "atom:content"

        if hasattr(entry, "content_encoded") and entry.content_encoded:
            if (
                isinstance(entry.content_encoded, str)
                and entry.content_encoded.strip()
            ):
                return entry.content_encoded, "content:encoded"

        for attr_name in ["content_encoded", "content"]:
            if hasattr(entry, attr_name):
                content_value = getattr(entry, attr_name)
                if isinstance(content_value, str) and content_value.strip():
                    return content_value, "content:encoded"

        return None, None

    def extract_author_from_entry(self, entry: Any) -> str | None:
        """Extract author from RSS/ATOM entry."""
        if hasattr(entry, "author"):
            author = getattr(entry, "author", "")
            if author:
                if isinstance(author, dict):
                    author_name = author.get("name", "")
                    if author_name:
                        return str(author_name)
                    for field in ["email", "uri"]:
                        field_value = author.get(field, "")
                        if field_value and "@" not in field_value:
                            return str(field_value)
                elif isinstance(author, str):
                    return str(author)
                elif isinstance(author, list) and author:
                    first_author = author[0]
                    if isinstance(first_author, dict):
                        author_name = first_author.get("name", "")
                        if author_name:
                            return str(author_name)
                    elif isinstance(first_author, str):
                        return str(first_author)

        if hasattr(entry, "author"):
            author = getattr(entry, "author", "")
            if author:
                return str(author)

        for field in ["dc_creator", "creator", "name"]:
            if hasattr(entry, field):
                value = getattr(entry, field)
                if value:
                    if isinstance(value, list):
                        authors = [str(v) for v in value if v]
                        return ", ".join(authors) if authors else None
                    return str(value)

        return None

    def extract_categories_from_entry(self, entry: Any) -> list[str]:
        """Extract categories from RSS/ATOM entry."""
        categories = []

        if hasattr(entry, "tags") and entry.tags:
            for tag in entry.tags:
                if isinstance(tag, dict):
                    term = tag.get("term")
                    if term:
                        categories.append(str(term))
                elif isinstance(tag, str):
                    categories.append(tag)

        if hasattr(entry, "category") and entry.category:
            if isinstance(entry.category, list):
                for cat in entry.category:
                    if cat:
                        categories.append(str(cat))
            elif isinstance(entry.category, str):
                categories.append(entry.category)

        if hasattr(entry, "subject") and entry.subject:
            if isinstance(entry.subject, list):
                for subject in entry.subject:
                    if subject:
                        categories.append(str(subject))
            elif isinstance(entry.subject, str):
                categories.append(entry.subject)

        for field in ["dc_subject", "subject"]:
            if hasattr(entry, field):
                value = getattr(entry, field)
                if value:
                    if isinstance(value, list):
                        for item in value:
                            if item:
                                categories.append(str(item))
                    else:
                        categories.append(str(value))

        return list(dict.fromkeys(categories))

    def extract_publish_date(self, entry: Any) -> datetime | None:
        """Extract publish date from RSS/ATOM entry."""
        import time

        def time_struct_to_dt(time_struct: Any) -> datetime | None:
            if time_struct and len(time_struct) >= 9:
                try:
                    timestamp = time.mktime(time_struct) - time_struct[8] * 60
                    return datetime.fromtimestamp(timestamp, tz=UTC)
                except (ValueError, OSError, OverflowError) as e:
                    logger.warning(
                        f"Error converting time struct to datetime: {e}"
                    )
            return None

        def parse_string_date(date_str: str | None) -> datetime | None:
            if not date_str or not isinstance(date_str, str):
                return None
            try:
                if feedparser_parse_date:
                    parsed = feedparser_parse_date(date_str)
                    if parsed:
                        return time_struct_to_dt(parsed)
                for fmt in (
                    "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%d %H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%SZ",
                ):
                    try:
                        dt = datetime.strptime(date_str.strip(), fmt)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=UTC)
                        return dt
                    except ValueError:
                        continue
            except Exception as e:
                logger.debug(
                    "Failed to parse date string",
                    date_str=date_str,
                    error=str(e),
                )
            return None

        logger = structlog.get_logger()

        date_fields = [
            "published_parsed",
            "updated_parsed",
            "created_parsed",
        ]

        for field in date_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field, None)
                if time_struct:
                    dt = time_struct_to_dt(time_struct)
                    if dt:
                        logger.debug(
                            "Extracted date from field", field=field, date=dt
                        )
                        return dt

        string_date_fields = [
            "published",
            "updated",
            "created",
        ]

        for field in string_date_fields:
            if hasattr(entry, field):
                date_str = getattr(entry, field, None)
                if date_str:
                    dt = parse_string_date(date_str)
                    if dt:
                        logger.debug(
                            "Extracted date from field", field=field, date=dt
                        )
                        return dt

        for field in ["date", "pubDate"]:
            if hasattr(entry, field):
                date_str = getattr(entry, field, None)
                if date_str:
                    dt = parse_string_date(date_str)
                    if dt:
                        logger.debug(
                            "Extracted date from field", field=field, date=dt
                        )
                        return dt

        logger.debug("No valid publish date found in entry")
        return None

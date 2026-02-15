"""RSS/ATOM feed metadata extraction utilities.

This module handles feed-level extraction (not entry-level).
For entry-level extraction, use entry_content.py.
"""

from typing import Any

import structlog

logger = structlog.get_logger()


class FeedExtractor:
    """Extracts structured metadata from RSS/Atom/RDF feed objects."""

    @staticmethod
    def detect_feed_type(feed: Any) -> str:
        """Detect feed type (RSS, Atom, RDF) from feedparser feed object.

        Args:
            feed: feedparser feed object.

        Returns:
            Feed type: 'rss', 'atom', or 'rdf'.

        """
        feed_type = "rss"
        if hasattr(feed, "version") and feed.version:
            if "atom" in feed.version.lower():
                feed_type = "atom"
            elif "rdf" in feed.version.lower():
                feed_type = "rdf"
            elif "rss" in feed.version.lower():
                feed_type = "rss"

        return feed_type

    @staticmethod
    def extract_title(feed: Any) -> str:
        """Extract feed title with fallback handling.

        Args:
            feed: feedparser feed object.

        Returns:
            Feed title or empty string.

        """
        title = feed.feed.get("title", "")
        return str(title) if title else ""

    @staticmethod
    def extract_description(feed: Any) -> str | None:
        """Extract feed description with reasonable length limit.

        Returns None if description is too long (>500 chars) to avoid
        storing excessive content as metadata.

        Args:
            feed: feedparser feed object.

        Returns:
            Feed description or None.

        """
        raw_description = feed.feed.get("description", "")

        if raw_description and len(str(raw_description)) < 500:
            return str(raw_description).strip()

        return None

    @staticmethod
    def extract_language(feed: Any) -> str | None:
        """Extract feed language with Dublin Core support.

        Priority order:
        1. RSS language tag
        2. Dublin Core language tag
        3. Other language fields

        Args:
            feed: feedparser feed object

        Returns:
            Language code string (ISO 639-1) or None
            Format: xx or xx-XX (lowercase language, optional uppercase country)

        """
        try:
            if hasattr(feed, "feed") and feed.feed:
                if hasattr(feed.feed, "language") and feed.feed.language:
                    language = str(feed.feed.language).strip()
                    if language:
                        return FeedExtractor._normalize_language_code(language)

                if hasattr(feed.feed, "dc_language") and feed.feed.dc_language:
                    language = str(feed.feed.dc_language).strip()
                    if language:
                        return FeedExtractor._normalize_language_code(language)

                for field in ["language", "dc_language"]:
                    if hasattr(feed.feed, field):
                        value = getattr(feed.feed, field)
                        if value:
                            language = str(value).strip()
                            if language:
                                return FeedExtractor._normalize_language_code(
                                    language
                                )

        except Exception as e:
            logger.debug("Error extracting feed language", error=str(e))

        return None

    @staticmethod
    def _normalize_language_code(language: str) -> str:
        """Normalize language code to match database constraint.

        Converts en-gb to en-GB format (lowercase language, uppercase country).

        Args:
            language: Raw language code (e.g., 'en-gb', 'EN-GB', 'en-US')

        Returns:
            Normalized language code (e.g., 'en-GB', 'en')

        """
        if not language:
            return language

        parts = language.split("-")
        if len(parts) == 1:
            return parts[0].lower()[:2]

        lang = parts[0].lower()[:2]
        country = parts[1].upper()[:2]
        return f"{lang}-{country}"

    @staticmethod
    def extract_website(feed: Any) -> str | None:
        """Extract the website URL from the feed.

        Args:
            feed: feedparser feed object.

        Returns:
            Website URL or None.

        """
        try:
            if hasattr(feed, "feed") and feed.feed:
                if hasattr(feed.feed, "link") and feed.feed.link:
                    link = feed.feed.link
                    if isinstance(link, str):
                        return link

                if hasattr(feed.feed, "links") and feed.feed.links:
                    for link_obj in feed.feed.links:
                        if (
                            hasattr(link_obj, "rel")
                            and link_obj.rel == "alternate"
                            and hasattr(link_obj, "href")
                        ):
                            return str(link_obj.href)

        except Exception as e:
            logger.debug("Error extracting feed website", error=str(e))

        return None

    @staticmethod
    def extract_feed_metadata(feed: Any) -> dict[str, str | None]:
        """Extract all feed metadata in a single call.

        Args:
            feed: feedparser feed object.

        Returns:
            Dictionary with title, description, language, and feed_type.

        """
        return {
            "title": FeedExtractor.extract_title(feed),
            "description": FeedExtractor.extract_description(feed),
            "language": FeedExtractor.extract_language(feed),
            "feed_type": FeedExtractor.detect_feed_type(feed),
        }

    @staticmethod
    def validate_feed_structure(feed: Any) -> tuple[bool, str | None]:
        """Validate that a feed has the minimum required structure.

        Checks:
        - Feed object exists
        - Feed has at least one entry

        Args:
            feed: feedparser feed object.

        Returns:
            Tuple of (is_valid, error_message).

        """
        if not feed.feed:
            return False, "no_feed_data"

        if not feed.entries:
            return False, "no_entries"

        return True, None

    @staticmethod
    def check_bozo_flags(feed: Any) -> tuple[bool, str | None]:
        """Check feedparser bozo flags for parsing errors.

        Args:
            feed: feedparser feed object.

        Returns:
            Tuple of (has_errors, error_message).

        """
        if feed.bozo and feed.bozo_exception:
            error_msg = str(feed.bozo_exception)
            logger.debug(
                "Feed has bozo flag",
                error=error_msg,
                error_type=type(feed.bozo_exception).__name__,
            )
            return True, "parsing_error"

        return False, None

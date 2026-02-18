"""RSS/ATOM feed metadata extraction utilities."""

from typing import Any

import structlog

logger = structlog.get_logger()


class FeedExtractor:
    """Extracts structured metadata from RSS/Atom/RDF feed objects."""

    @staticmethod
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

    @staticmethod
    def extract_title(feed: Any) -> str:
        """Extract feed title with fallback handling."""
        title = feed.feed.get("title", "")
        return str(title) if title else ""

    @staticmethod
    def extract_description(feed: Any) -> str | None:
        """Extract feed description with reasonable length limit."""
        raw_description = feed.feed.get("description", "")

        if raw_description and len(str(raw_description)) < 500:
            return str(raw_description).strip()

        return None

    @staticmethod
    def extract_language(feed: Any) -> str | None:
        """Extract feed language with Dublin Core support."""
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
        """Normalize language code to match database constraint."""
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
        """Extract the website URL from the feed."""
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
        """Extract all feed metadata in a single call."""
        return {
            "title": FeedExtractor.extract_title(feed),
            "description": FeedExtractor.extract_description(feed),
            "language": FeedExtractor.extract_language(feed),
            "feed_type": FeedExtractor.detect_feed_type(feed),
        }

    @staticmethod
    def validate_feed_structure(feed: Any) -> tuple[bool, str | None]:
        """Validate that a feed has the minimum required structure."""
        if not feed.feed:
            return False, "no_feed_data"

        if not feed.entries:
            return False, "no_entries"

        return True, None

    @staticmethod
    def check_bozo_flags(feed: Any) -> tuple[bool, str | None]:
        """Check feedparser bozo flags for parsing errors."""
        if feed.bozo and feed.bozo_exception:
            error_msg = str(feed.bozo_exception)
            logger.debug(
                "Feed has bozo flag",
                error=error_msg,
                error_type=type(feed.bozo_exception).__name__,
            )
            return True, "parsing_error"

        return False, None

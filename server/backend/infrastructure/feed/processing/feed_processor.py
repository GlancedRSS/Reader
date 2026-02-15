"""Feed parsing and article creation infrastructure for RSS/Atom feeds."""

import html
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.app import settings
from backend.infrastructure.feed.parsing.content.media import MediaExtractor
from backend.infrastructure.feed.parsing.entry_content import EntryExtractor
from backend.infrastructure.feed.parsing.feed_metadata import FeedExtractor
from backend.infrastructure.feed.processing.article_processor import (
    ArticleProcessor,
)
from backend.infrastructure.parsers import HTMLCleaner
from backend.infrastructure.repositories.feed import FeedRepository
from backend.schemas.feeds import DiscoveryFeedCreateRequest, FeedUpdateRequest
from backend.utils.date_utils import parse_iso_datetime

logger = structlog.get_logger()


class FeedProcessor:
    """Infrastructure for parsing RSS/Atom feeds and creating articles."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the feed processor.

        Args:
            db: Async database session.

        """
        self.db = db
        self.html_cleaner = HTMLCleaner()
        self.media_extractor = MediaExtractor()
        self.entry_extractor = EntryExtractor()
        self.repository = FeedRepository(db)
        self.article_processor = ArticleProcessor(db)

    def extract_feed_content(
        self, entry: Any
    ) -> tuple[
        str,
        str | None,
        str | None,
        str | None,
        list[str],
        str | None,
        dict[str, Any],
    ]:
        """Extract content, image, author, categories, and platform_metadata from RSS feed entry.

        This method inlines the logic from ContentProcessor.

        Args:
            entry: RSS/Atom feed entry object.

        Returns:
            Tuple of (clean_content, search_content, image_url, author, categories, content_source, platform_metadata).

        """
        content, content_source = (
            self.entry_extractor.extract_content_from_entry(entry)
        )

        image_url = self.media_extractor.extract_image_from_entry(entry)

        if not image_url:
            image_url = (
                self.media_extractor.extract_image_from_summary_description(
                    entry
                )
            )

        if not image_url and content:
            image_url = self.media_extractor.extract_image_from_html(content)

        author = self.entry_extractor.extract_author_from_entry(entry)
        categories = self.entry_extractor.extract_categories_from_entry(entry)
        platform_metadata = self.media_extractor.extract_metadata_from_entry(
            entry
        )

        if image_url:
            logger.info(
                "Extracted media_url from feed entry",
                link=entry.get("link", ""),
                media_url=image_url,
            )

        if platform_metadata:
            logger.debug(
                "Extracted platform_metadata from feed entry",
                link=entry.get("link", ""),
                metadata_keys=list(platform_metadata.keys()),
            )

        if content:
            clean_content = self.html_cleaner.clean_html(content)
            search_content = self.html_cleaner.html_to_text(content)
        else:
            clean_content = ""
            search_content = ""

        return (
            clean_content,
            search_content,
            image_url,
            author,
            categories,
            content_source,
            platform_metadata,
        )

    async def create_feed(self, feed_data: DiscoveryFeedCreateRequest) -> Any:
        """Create a new feed using unified feed parsing approach.

        Args:
            feed_data: The feed creation request data.

        Returns:
            The created Feed object.

        """
        logger.info("Starting feed creation", url=feed_data.url)
        try:
            existing = await self.repository.get_feed_by_url(feed_data.url)
            if existing:
                logger.info(
                    "Feed already exists",
                    url=feed_data.url,
                    feed_id=existing.id,
                )
                return existing

            feed_info = await self._parse_feed_content(feed_data.url)

            try:
                feed_record = await self.repository.create_feed(
                    url=feed_data.url,
                    title=str(feed_info["title"] or feed_data.title or ""),
                    description=feed_info.get("description"),
                    feed_type=feed_info["feed_type"],
                    language=feed_info.get("language"),
                    website=feed_info["website"],
                    has_articles=bool(feed_info.get("articles")),
                )
            except Exception:
                existing = await self.repository.get_feed_by_url(feed_data.url)
                if existing:
                    logger.info(
                        "Feed created by another worker, using existing feed",
                        url=feed_data.url,
                        feed_id=existing.id,
                    )
                    return existing
                raise

            articles_data = feed_info.get("articles", [])
            last_update: datetime | None = None

            if articles_data:
                published_dates = [
                    parse_iso_datetime(a.get("published_at"))
                    for a in articles_data
                    if a.get("published_at")
                ]
                if published_dates:
                    last_update = max(
                        d for d in published_dates if d is not None
                    )

                (
                    created_count,
                    _new_article_ids,
                    all_article_ids,
                ) = await self.article_processor.process_feed_articles(
                    feed_record.id, articles_data
                )
                if all_article_ids:
                    updated_feed = await self.repository.update_feed(
                        feed_record.id, {"latest_articles": all_article_ids}
                    )
                    if updated_feed:
                        feed_record = updated_feed
            else:
                created_count = 0

            if last_update:
                feed_record.last_update = last_update

            logger.info(
                "Feed creation completed successfully",
                feed_id=feed_record.id,
                url=feed_data.url,
                feed_title=feed_info["title"],
                articles_created=created_count,
                last_update=last_update,
            )

            return feed_record

        except Exception as e:
            logger.exception(
                "Feed creation failed",
                url=feed_data.url,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    async def update_feed(
        self, feed_id: UUID, feed_data: FeedUpdateRequest
    ) -> Any | None:
        """Update feed metadata.

        Args:
            feed_id: The feed ID to update.
            feed_data: The feed update request data.

        Returns:
            The updated Feed object, or None if not found.

        """
        logger.info("Starting feed update", feed_id=feed_id)

        try:
            feed = await self.repository.get_feed_by_id(feed_id)
            if not feed:
                logger.warning("Feed not found for update", feed_id=feed_id)
                return None

            update_data: dict[str, Any] = {}
            if feed_data.title is not None:
                update_data["title"] = feed_data.title
            if feed_data.description is not None:
                update_data["description"] = feed_data.description

            updated_feed = await self.repository.update_feed(
                feed_id, update_data
            )

            logger.info(
                "Feed update completed successfully",
                feed_id=feed_id,
                update_fields=list(update_data.keys()),
            )
            return updated_feed

        except Exception as e:
            logger.exception(
                "Feed update failed",
                feed_id=feed_id,
                error=str(e),
            )
            raise

    async def delete_feed(self, feed_id: UUID) -> bool:
        """Delete a feed and all its articles.

        Args:
            feed_id: The feed ID to delete.

        Returns:
            True if feed was deleted, False if not found.

        """
        logger.info("Starting feed deletion", feed_id=feed_id)

        try:
            feed = await self.repository.get_feed_by_id(feed_id)
            if not feed:
                logger.warning("Feed not found for deletion", feed_id=feed_id)
                return False

            await self.repository.delete_feed(feed)
            logger.info(
                "Feed deletion completed successfully",
                feed_id=feed_id,
            )
            return True

        except Exception as e:
            logger.exception(
                "Error deleting feed", feed_id=feed_id, error=str(e)
            )
            raise

    async def get_feed_by_id(self, feed_id: UUID) -> Any | None:
        """Get feed by ID.

        Args:
            feed_id: The feed ID.

        Returns:
            The Feed object if found, None otherwise.

        """
        return await self.repository.get_feed_by_id(feed_id)

    async def refresh_feed(self, feed_id: UUID) -> dict[str, Any]:
        """Refresh feed articles.

        Args:
            feed_id: The feed ID to refresh.

        Returns:
            Dictionary with feed_id, articles_created, last_update, or error key if failed.

        """
        logger.info("Starting feed refresh", feed_id=feed_id)

        try:
            feed = await self.repository.get_feed_by_id(feed_id)
            if not feed:
                logger.warning("Feed not found for refresh", feed_id=feed_id)
                return {"error": "Feed not found"}

            canonical_url = feed.canonical_url
            if not canonical_url:
                return {"error": "Feed has no canonical URL"}

            feed_info = await self._parse_feed_content(canonical_url)

            articles_data = feed_info.get("articles", [])
            last_update: datetime | None = None

            if articles_data:
                published_dates = [
                    parse_iso_datetime(a.get("published_at"))
                    for a in articles_data
                    if a.get("published_at")
                ]
                if published_dates:
                    last_update = max(
                        d for d in published_dates if d is not None
                    )

                (
                    created_count,
                    _new_article_ids,
                    all_article_ids,
                ) = await self.article_processor.process_feed_articles(
                    feed_id, articles_data
                )
                if all_article_ids:
                    await self.repository.update_feed(
                        feed_id, {"latest_articles": all_article_ids}
                    )
            else:
                created_count = 0

            update_data: dict[str, Any] = {
                "last_fetched_at": datetime.now(UTC),
            }
            if feed_info.get("title"):
                update_data["title"] = feed_info["title"]
            if feed_info.get("description"):
                update_data["description"] = feed_info["description"]
            if feed_info.get("website"):
                update_data["website"] = feed_info["website"]
            if last_update is not None:
                update_data["last_update"] = last_update

            if update_data:
                await self.repository.update_feed(feed_id, update_data)

            logger.info(
                "Feed refresh completed",
                feed_id=feed_id,
                articles_created=created_count,
                last_update=last_update,
            )

            return {
                "feed_id": feed_id,
                "articles_created": created_count,
                "last_update": last_update,
                "status": "success",
            }

        except Exception as e:
            logger.exception(
                "Feed refresh failed",
                feed_id=feed_id,
                error=str(e),
            )
            return {"error": str(e)}

    async def _parse_feed_content(
        self, url: str, timeout: float | None = None
    ) -> dict[str, Any]:
        """Parse RSS/Atom feed content and extract articles.

        Args:
            url: The feed URL to parse.
            timeout: Optional timeout in seconds (uses default if not specified).

        Returns:
            Dictionary with feed metadata and articles list.

        """
        logger.info("Parsing feed content", url=url)

        async with httpx.AsyncClient(
            timeout=timeout or settings.request_timeout
        ) as client:
            headers = {
                "User-Agent": settings.user_agent,
                "Accept": "application/rss+xml, application/atom+xml, application/rdf+xml, text/xml, application/xml;q=0.9, text/html;q=0.8, */*;q=0.1",
            }
            response = await client.get(
                url, headers=headers, follow_redirects=True
            )
            response.raise_for_status()

            import feedparser

            feed = feedparser.parse(response.content)

            feed_metadata = FeedExtractor.extract_feed_metadata(feed)

            feed_language = FeedExtractor.extract_language(feed)

            website = FeedExtractor.extract_website(feed)

            articles_data = []
            if feed.entries:
                articles_data = self._parse_feed_entries(feed)

            if not feed_metadata.get("title"):
                raise ValueError(
                    f"URL does not appear to be a valid RSS/Atom feed: {url}. "
                    f"Please provide a direct feed URL (e.g., {url.rstrip('/')}/rss/index.xml or {url.rstrip('/')}/feed)"
                )

            return {
                "title": feed_metadata["title"],
                "description": feed_metadata["description"],
                "feed_type": feed_metadata["feed_type"],
                "language": feed_language,
                "website": website,
                "articles": articles_data,
            }

    def _parse_feed_entries(self, feed: Any) -> list[dict[str, Any]]:
        """Parse articles from feed entries.

        Args:
            feed: The parsed feed object.

        Returns:
            List of article data dictionaries.

        """
        articles_data = []
        max_articles = 50

        for entry in feed.entries[:max_articles]:
            published_date = self.entry_extractor.extract_publish_date(entry)

            (
                clean_content,
                search_content,
                media_url,
                author,
                categories,
                _,
                platform_metadata,
            ) = self.extract_feed_content(entry)

            raw_summary = entry.get("summary", "") or entry.get(
                "description", ""
            )
            summary = (
                self.html_cleaner.html_to_text(raw_summary)
                if raw_summary
                else ""
            )

            article_data: dict[str, Any] = {
                "title": html.unescape(entry.get("title", "")),
                "url": entry.get("link", ""),
                "summary": summary,
                "content": clean_content,
                "search_content": search_content or summary,
                "author": author,
                "media_url": media_url,
                "published_at": published_date.isoformat()
                if published_date
                else None,
                "categories": categories,
                "platform_metadata": platform_metadata,
            }

            articles_data.append(article_data)

        return articles_data

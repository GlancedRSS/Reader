"""Article processing infrastructure for article deduplication and processing operations."""

import re
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.feed.processing.partition import Partition
from backend.infrastructure.repositories.tag import UserTagRepository
from backend.models import (
    Article,
    ArticleSource,
    UserFeed,
)
from backend.utils.date_utils import parse_iso_datetime
from backend.utils.url_normalizer import normalize_url

logger = structlog.get_logger()


class ArticleProcessor:
    """Infrastructure for processing articles with deduplication."""

    def __init__(self, db: AsyncSession):
        """Initialize the article processor."""
        self.db = db
        self.partition_service = Partition(db)
        self.tag_repository = UserTagRepository(db)

    async def process_feed_articles(
        self,
        feed_id: UUID,
        articles_data: list[dict[str, Any]],
    ) -> tuple[int, list[UUID], list[UUID]]:
        """Process feed articles with deduplication and create junction relationships."""
        created_count = 0
        relationship_count = 0
        new_article_ids: list[UUID] = []
        existing_articles_for_assignment: list[UUID] = []
        all_fetched_article_ids: list[UUID] = []
        articles_needing_tags: list[tuple[UUID, list[str]]] = []

        try:
            logger.info(
                f"Pre-analyzing {len(articles_data)} articles for partition creation..."
            )
            created_partitions = (
                await self.partition_service.analyze_and_create_partitions(
                    articles_data
                )
            )

            if created_partitions:
                logger.info(
                    f"Successfully pre-created {len(created_partitions)} partitions for feed processing"
                )

            for article_data in articles_data:
                article_url = article_data.get("url", "")
                if not article_url:
                    continue

                canonical_url = normalize_url(article_url)

                existing_stmt = (
                    select(Article)
                    .where(Article.canonical_url == canonical_url)
                    .with_for_update()
                )
                existing_result = await self.db.execute(existing_stmt)
                existing_article = existing_result.scalar_one_or_none()

                if existing_article:
                    all_fetched_article_ids.append(existing_article.id)

                    relationship_stmt = select(ArticleSource).where(
                        and_(
                            ArticleSource.article_id == existing_article.id,
                            ArticleSource.feed_id == feed_id,
                        )
                    )
                    relationship_result = await self.db.execute(
                        relationship_stmt
                    )
                    existing_relationship = (
                        relationship_result.scalar_one_or_none()
                    )

                    if not existing_relationship:
                        relationship = ArticleSource(
                            article_id=existing_article.id, feed_id=feed_id
                        )
                        self.db.add(relationship)
                        relationship_count += 1
                        existing_articles_for_assignment.append(
                            existing_article.id
                        )
                        logger.info(
                            f"Added existing article to feed: {existing_article.title or canonical_url}"
                        )
                    else:
                        logger.debug(
                            f"Article already in feed: {existing_article.title or canonical_url}"
                        )

                else:
                    published_date = parse_iso_datetime(
                        article_data.get("published_at")
                    )

                    if published_date and published_date > datetime.now(UTC):
                        logger.warning(
                            f"Skipping article with future publication date: {article_data.get('title', canonical_url)} - {published_date}"
                        )
                        continue

                    categories = article_data.get("categories", [])
                    source_tags = []
                    if categories:
                        for category in categories:
                            if category and category.strip():
                                tag_names = [
                                    name.strip()
                                    for name in category.split(",")
                                    if name.strip()
                                ]
                                source_tags.extend(tag_names)

                    article = Article(
                        canonical_url=canonical_url,
                        title=article_data.get("title", ""),
                        author=article_data.get("author", ""),
                        summary=article_data.get("summary", "")[:2000],
                        content=article_data.get("content", "") or None,
                        source_tags=source_tags,
                        media_url=article_data.get("media_url", ""),
                        platform_metadata=article_data.get(
                            "platform_metadata", {}
                        ),
                        published_at=published_date,
                    )

                    logger.info(
                        f"Created article with media_url: {article.media_url}",
                        canonical_url=canonical_url,
                        media_url=article.media_url,
                        raw_media_url_key=article_data.get(
                            "media_url", "MISSING"
                        ),
                    )

                    try:
                        self.db.add(article)
                        await self.db.flush()
                    except Exception as e:
                        error_str = str(e).lower()
                        if "duplicate" in error_str or "unique" in error_str:
                            logger.info(
                                f"Article already exists (created by concurrent process): {canonical_url}"
                            )
                            existing_stmt = select(Article).where(
                                Article.canonical_url == canonical_url
                            )
                            existing_result = await self.db.execute(
                                existing_stmt
                            )
                            existing_article = (
                                existing_result.scalar_one_or_none()
                            )
                            if existing_article:
                                article = existing_article
                            else:
                                continue
                        elif (
                            "partition" in error_str
                            and "articles" in error_str
                            and published_date
                        ):
                            try:
                                partition_month = published_date.strftime(
                                    "%Y_%m"
                                )
                                start_date = published_date.replace(
                                    day=1,
                                    hour=0,
                                    minute=0,
                                    second=0,
                                    microsecond=0,
                                )
                                end_date = (
                                    start_date + timedelta(days=32)
                                ).replace(day=1)

                                if not re.match(
                                    r"^\d{4}_\d{2}$", partition_month
                                ):
                                    raise ValueError(
                                        f"Invalid partition_month format: {partition_month}"
                                    )

                                table_name = f"articles_{partition_month}"
                                full_partition_name = f"content.{table_name}"

                                partition_sql = text(
                                    f"""
                                    CREATE TABLE IF NOT EXISTS {full_partition_name}
                                    PARTITION OF content.articles
                                    FOR VALUES FROM (:start_date)
                                    TO (:end_date)
                                """
                                )
                                await self.db.execute(
                                    partition_sql,
                                    {
                                        "start_date": start_date.isoformat(),
                                        "end_date": end_date.isoformat(),
                                    },
                                )

                                logger.info(
                                    f"Auto-created partition articles_{partition_month} for date {published_date}"
                                )

                                self.db.add(article)
                                await self.db.flush()

                            except Exception as partition_error:
                                logger.exception(
                                    f"Failed to create partition for {published_date}: {partition_error}"
                                )
                                raise e from None
                        else:
                            raise e

                    relationship = ArticleSource(
                        article_id=article.id, feed_id=feed_id
                    )
                    self.db.add(relationship)

                    if source_tags:
                        articles_needing_tags.append((article.id, source_tags))

                    all_fetched_article_ids.append(article.id)
                    created_count += 1
                    new_article_ids.append(article.id)

                    logger.info(
                        f"Created new article: {article.title or canonical_url}"
                    )

            if new_article_ids:
                await self._create_user_states_for_subscribers(
                    feed_id, new_article_ids
                )

            if existing_articles_for_assignment:
                await self._create_user_states_for_subscribers(
                    feed_id, existing_articles_for_assignment
                )

            for article_id, source_tags in articles_needing_tags:
                await self._create_tags_for_subscribers(
                    feed_id, article_id, source_tags
                )

            if created_count > 0 or relationship_count > 0:
                logger.info(
                    f"Processed feed articles - Created: {created_count}, "
                    f"Added relationships: {relationship_count}, "
                    f"Assigned existing articles: {len(existing_articles_for_assignment)}, "
                    f"feed_id: {feed_id}"
                )

            return created_count, new_article_ids, all_fetched_article_ids

        except Exception as e:
            logger.exception(
                "Error processing articles", error=str(e), feed_id=feed_id
            )
            raise

    async def _create_user_states_for_subscribers(
        self, feed_id: UUID, article_ids: list[UUID]
    ) -> None:
        """Create user_article_states for all active subscribers of a feed."""
        subscribers_stmt = select(UserFeed.user_id).where(
            and_(
                UserFeed.feed_id == feed_id,
                UserFeed.is_active,
            )
        )
        subscribers_result = await self.db.execute(subscribers_stmt)
        subscriber_ids = [row[0] for row in subscribers_result.all()]

        if not subscriber_ids:
            logger.debug("No active subscribers for feed", feed_id=feed_id)
            return

        values_list = []
        for user_id in subscriber_ids:
            for article_id in article_ids:
                values_list.append(
                    {"user_id": user_id, "article_id": article_id}
                )

        query = text("""
            INSERT INTO content.user_articles (user_id, article_id, is_read, read_later)
            VALUES (:user_id, :article_id, false, false)
            ON CONFLICT (user_id, article_id)
            DO NOTHING
        """)
        for values in values_list:
            await self.db.execute(query, values)

        logger.info(
            f"Created user_article_states for feed {feed_id}: "
            f"{len(subscriber_ids)} subscribers, {len(article_ids)} articles"
        )

    async def _create_tags_for_subscribers(
        self, feed_id: UUID, article_id: UUID, source_tags: list[str]
    ) -> None:
        """Create tags for all subscribers of a feed from article source_tags."""
        if not source_tags:
            return

        subscribers_stmt = select(UserFeed.user_id).where(
            and_(
                UserFeed.feed_id == feed_id,
                UserFeed.is_active,
            )
        )
        subscribers_result = await self.db.execute(subscribers_stmt)
        subscriber_ids = [row[0] for row in subscribers_result.all()]

        if not subscriber_ids:
            logger.debug("No active subscribers for feed", feed_id=feed_id)
            return

        for user_id in subscriber_ids:
            for tag_name in source_tags:
                tag = await self.tag_repository.get_or_create_tag(
                    user_id=user_id,
                    name=tag_name,
                )
                await self.tag_repository.add_tags_to_article(
                    article_id=article_id, tag_ids=[tag.id], user_id=user_id
                )

        logger.info(
            f"Created tags for article {article_id}: "
            f"{len(subscriber_ids)} subscribers, {len(source_tags)} tags"
        )

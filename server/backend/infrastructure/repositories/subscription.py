"""Repository for subscription-related data access operations."""

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.repositories.tag import UserTagRepository
from backend.models import (
    Article,
    ArticleSource,
    Feed,
    UserArticle,
)

logger = structlog.get_logger()


class SubscriptionRepository:
    """Repository for subscription and article-tag relationship data access."""

    def __init__(self, db: AsyncSession):
        """Initialize the subscription repository."""
        self.db = db
        self.tag_repository = UserTagRepository(db)

    async def get_articles_for_feed(self, feed_id: UUID) -> list[Article]:
        """Get all articles for a specific feed."""
        articles_query = (
            select(Article)
            .join(ArticleSource)
            .where(ArticleSource.feed_id == feed_id)
        )

        articles_result = await self.db.execute(articles_query)
        return list(articles_result.scalars().all())

    async def get_article_ids_for_feed(self, feed_id: UUID) -> list[UUID]:
        """Get all article IDs for a specific feed."""
        articles_query = (
            select(Article.id)
            .join(
                ArticleSource,
                Article.id == ArticleSource.article_id,
            )
            .where(ArticleSource.feed_id == feed_id)
        )

        articles_result = await self.db.execute(articles_query)
        return list(articles_result.scalars().all())

    async def get_recent_article_ids_for_feed(
        self, feed_id: UUID, since_timestamp: datetime
    ) -> list[UUID]:
        """Get article IDs from a feed's latest_articles array."""
        logger.info(
            "Getting recent article IDs for feed",
            feed_id=str(feed_id),
            since_timestamp=since_timestamp.isoformat(),
        )

        feed_query = select(Feed.latest_articles).where(Feed.id == feed_id)
        feed_result = await self.db.execute(feed_query)
        latest_articles = feed_result.scalar_one_or_none()

        if latest_articles:
            result: list[UUID] = latest_articles
        else:
            result = []

        logger.info(
            "Latest articles from feed",
            feed_id=str(feed_id),
            article_count=len(result),
        )

        return result

    async def bulk_upsert_user_article_states(
        self, user_id: UUID, article_ids: list[UUID]
    ) -> int:
        """Bulk insert UserArticle records with conflict handling."""
        if not article_ids:
            return 0

        values = []
        for article_id in article_ids:
            values.append(f"('{user_id}', '{article_id}', false, false)")

        query = f"""
            INSERT INTO content.user_articles (user_id, article_id, is_read, read_later)
            VALUES {",".join(values)}
            ON CONFLICT (user_id, article_id)
            DO NOTHING
        """

        result = await self.db.execute(text(query))
        return result.rowcount if hasattr(result, "rowcount") else 0

    async def recalculate_subscription_unread_count(
        self, subscription_id: UUID
    ) -> int | None:
        """Call stored procedure to recalculate subscription unread count."""
        try:
            recalc_result = await self.db.execute(
                text(
                    "SELECT content.recalculate_subscription_unread_count(:subscription_id)"
                ),
                {"subscription_id": subscription_id},
            )
            return recalc_result.scalar()
        except Exception as e:
            logger.warning(
                "Could not calculate initial unread count for subscription",
                subscription_id=subscription_id,
                error=str(e),
            )
            return None

    async def create_article_tag_relationship(
        self, article_id: UUID, tag_id: UUID, user_id: UUID
    ) -> None:
        """Create a junction relationship between article and tag."""
        await self.tag_repository.add_tags_to_article(
            article_id, [tag_id], user_id
        )

    async def get_unread_articles_for_user(
        self, user_id: UUID, older_than: datetime
    ) -> list[UserArticle]:
        """Get unread articles for a user older than a given date."""
        stmt = (
            select(UserArticle)
            .join(Article, UserArticle.article_id == Article.id)
            .where(UserArticle.user_id == user_id)
            .where(UserArticle.is_read.is_(False))
            .where(Article.published_at < older_than)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_articles_as_read(
        self,
        user_id: UUID,
        article_ids: list[UUID],
        read_at: datetime | None = None,
    ) -> int:
        """Mark articles as read for a user."""
        if not article_ids:
            return 0

        if read_at is None:
            read_at = datetime.now(UTC)

        result = await self.db.execute(
            select(UserArticle).where(
                UserArticle.user_id == user_id,
                UserArticle.article_id.in_(article_ids),
            )
        )
        user_articles = result.scalars().all()

        count = 0
        for ua in user_articles:
            ua.is_read = True
            ua.read_at = read_at
            count += 1

        return count

    async def bulk_mark_old_articles_as_read(
        self,
        cutoff_date_7days: datetime,
        cutoff_date_14days: datetime,
        cutoff_date_30days: datetime,
        read_at: datetime | None = None,
    ) -> dict[str, int]:
        """Bulk mark old articles as read for all users with auto-read enabled."""
        if read_at is None:
            read_at = datetime.now(UTC)

        query = text("""
            WITH articles_to_mark AS (
                SELECT ua.user_id, ua.article_id
                FROM content.user_articles ua
                JOIN accounts.users u ON ua.user_id = u.id
                JOIN personalization.user_preferences up ON up.user_id = u.id
                JOIN content.articles a ON ua.article_id = a.id
                WHERE ua.is_read = false
                  AND up.auto_mark_as_read IN ('7_days', '14_days', '30_days')
                  AND (
                      (up.auto_mark_as_read = '7_days' AND a.published_at < :cutoff_7)
                      OR (up.auto_mark_as_read = '14_days' AND a.published_at < :cutoff_14)
                      OR (up.auto_mark_as_read = '30_days' AND a.published_at < :cutoff_30)
                  )
            )
            UPDATE content.user_articles ua
            SET is_read = true,
                read_at = :read_at
            FROM articles_to_mark atm
            WHERE ua.user_id = atm.user_id
              AND ua.article_id = atm.article_id
            RETURNING
                (SELECT COUNT(DISTINCT user_id) FROM articles_to_mark) as users_affected,
                COUNT(*) as articles_marked
        """)

        result = await self.db.execute(
            query,
            {
                "cutoff_7": cutoff_date_7days,
                "cutoff_14": cutoff_date_14days,
                "cutoff_30": cutoff_date_30days,
                "read_at": read_at,
            },
        )

        row = result.fetchone()
        stats = {
            "users_affected": row[0] if row else 0,
            "articles_marked": row[1] if row else 0,
        }

        await self.db.commit()

        logger.info(
            "Bulk auto-mark as read completed",
            users_affected=stats["users_affected"],
            articles_marked=stats["articles_marked"],
        )

        return stats

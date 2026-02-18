"""Postgres-based full-text search using pg_trgm and tsvector."""

from collections import namedtuple
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import (
    and_,
    case,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import (
    ArticleTag,
    Feed,
    UserArticle,
    UserFeed,
    UserFolder,
    UserTag,
)

SearchRow = namedtuple(
    "SearchRow",
    [
        "id",
        "title",
        "summary",
        "media_url",
        "published_at",
        "created_at",
        "is_read",
        "read_later",
        "feeds",
        "relevance",
    ],
)


@dataclass
class SearchResult:
    """Result from articles search query execution."""

    articles: list[SearchRow]
    next_cursor: str | None
    has_more: bool


class SearchRepository:
    """Postgres-native search repository using full-text search and trigrams."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize search repository."""
        self.db = db

    async def search_feeds(
        self,
        query: str,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search user's feed subscriptions using trigram similarity."""
        ts_vector = func.to_tsvector("simple", UserFeed.title)

        words = query.strip().split()
        if len(words) > 1:
            prefix_query_str = " | ".join([f"{w}:*" for w in words])
            prefix_query = func.to_tsquery("simple", prefix_query_str)
        else:
            prefix_query = func.to_tsquery("simple", f"{query}:*")

        title_match = case((UserFeed.title.ilike(f"{query}%"), 1.0), else_=0.0)

        base_query = (
            select(
                UserFeed.id,
                UserFeed.title,
                Feed.website,
                UserFeed.is_active,
                UserFeed.is_pinned,
                UserFeed.unread_count,
                (
                    title_match + func.similarity(UserFeed.title, query) * 0.5
                ).label("relevance"),
            )
            .join(Feed, UserFeed.feed_id == Feed.id)
            .where(
                and_(
                    UserFeed.user_id == user_id,
                    or_(
                        ts_vector.op("@@")(prefix_query),  # Word-prefix match
                        UserFeed.title.op("%")(query),  # Fuzzy trigram on title
                    ),
                )
            )
        )

        final_query = base_query.order_by(
            title_match + func.similarity(UserFeed.title, query) * 0.5,
            Feed.last_update.desc(),
            UserFeed.created_at.desc(),
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = int(count_result.scalar() or 0)

        paginated_query = final_query.limit(limit).offset(offset)
        result = await self.db.execute(paginated_query)
        rows = result.all()

        data = []
        for row in rows:
            relevance = (
                float(row.relevance) if row.relevance is not None else 0.0
            )
            data.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "website": row.website,
                    "is_active": bool(row.is_active),
                    "is_pinned": bool(row.is_pinned),
                    "unread_count": row.unread_count or 0,
                    "_relevance": relevance,
                }
            )

        has_more = offset + limit < total

        return {
            "data": data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
            },
        }

    async def search_tags(
        self,
        query: str,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search user's tags using trigram similarity."""
        article_count_subq = (
            select(
                ArticleTag.user_tag_id,
                func.count(ArticleTag.id).label("article_count"),
            )
            .join(UserArticle, ArticleTag.user_article_id == UserArticle.id)
            .where(UserArticle.user_id == user_id)
            .group_by(ArticleTag.user_tag_id)
            .subquery()
        )

        ts_vector = func.to_tsvector("simple", UserTag.name)

        words = query.strip().split()
        if len(words) > 1:
            prefix_query_str = " | ".join([f"{w}:*" for w in words])
            prefix_query = func.to_tsquery("simple", prefix_query_str)
        else:
            prefix_query = func.to_tsquery("simple", f"{query}:*")

        base_query = (
            select(
                UserTag.id,
                UserTag.name,
                func.coalesce(article_count_subq.c.article_count, 0).label(
                    "article_count"
                ),
                (
                    case((UserTag.name.ilike(f"{query}%"), 1.0), else_=0.0)
                    + func.similarity(UserTag.name, query) * 0.5
                ).label("relevance"),
            )
            .outerjoin(
                article_count_subq,
                UserTag.id == article_count_subq.c.user_tag_id,
            )
            .where(
                and_(
                    UserTag.user_id == user_id,
                    or_(
                        ts_vector.op("@@")(prefix_query),
                        UserTag.name.op("%")(query),
                    ),
                )
            )
        )

        final_query = base_query.order_by(
            case((UserTag.name.ilike(f"{query}%"), 1.0), else_=0.0)
            + func.similarity(UserTag.name, query) * 0.5,
            UserTag.name.asc(),
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = int(count_result.scalar() or 0)

        paginated_query = final_query.limit(limit).offset(offset)
        result = await self.db.execute(paginated_query)
        rows = result.all()

        data = []
        for row in rows:
            relevance = (
                float(row.relevance) if row.relevance is not None else 0.0
            )
            data.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "article_count": row.article_count,
                    "_relevance": relevance,
                }
            )

        has_more = offset + limit < total

        return {
            "data": data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
            },
        }

    async def search_folders(
        self,
        query: str,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search user's folders using trigram similarity."""
        unread_count_subq = (
            select(
                UserFeed.folder_id,
                func.coalesce(func.sum(UserFeed.unread_count), 0).label(
                    "unread_count"
                ),
            )
            .where(
                and_(
                    UserFeed.user_id == user_id, UserFeed.folder_id.isnot(None)
                )
            )
            .group_by(UserFeed.folder_id)
            .subquery()
        )

        ts_vector = func.to_tsvector("simple", UserFolder.name)

        words = query.strip().split()
        if len(words) > 1:
            prefix_query_str = " | ".join([f"{w}:*" for w in words])
            prefix_query = func.to_tsquery("simple", prefix_query_str)
        else:
            prefix_query = func.to_tsquery("simple", f"{query}:*")

        base_query = (
            select(
                UserFolder.id,
                UserFolder.name,
                func.coalesce(unread_count_subq.c.unread_count, 0).label(
                    "unread_count"
                ),
                UserFolder.is_pinned,
                (
                    case((UserFolder.name.ilike(f"{query}%"), 1.0), else_=0.0)
                    + func.similarity(UserFolder.name, query) * 0.5
                ).label("relevance"),
            )
            .outerjoin(
                unread_count_subq,
                UserFolder.id == unread_count_subq.c.folder_id,
            )
            .where(
                and_(
                    UserFolder.user_id == user_id,
                    or_(
                        ts_vector.op("@@")(prefix_query),
                        UserFolder.name.op("%")(query),
                    ),
                )
            )
        )

        final_query = base_query.order_by(
            case((UserFolder.name.ilike(f"{query}%"), 1.0), else_=0.0)
            + func.similarity(UserFolder.name, query) * 0.5,
            UserFolder.name.asc(),
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = int(count_result.scalar() or 0)

        paginated_query = final_query.limit(limit).offset(offset)
        result = await self.db.execute(paginated_query)
        rows = result.all()

        data = []
        for row in rows:
            relevance = (
                float(row.relevance) if row.relevance is not None else 0.0
            )
            data.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "unread_count": row.unread_count,
                    "is_pinned": bool(row.is_pinned),
                    "_relevance": relevance,
                }
            )

        has_more = offset + limit < total

        return {
            "data": data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
            },
        }

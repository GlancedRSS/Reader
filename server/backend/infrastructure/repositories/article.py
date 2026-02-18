"""Repository for article state management and queries."""

from collections import namedtuple
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Select,
    and_,
    distinct,
    func,
    literal_column,
    nullslast,
    or_,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundError
from backend.models import (
    Article,
    ArticleSource,
    ArticleTag,
    Feed,
    User,
    UserArticle,
    UserFeed,
    UserTag,
)
from backend.utils.cursor import (
    create_article_cursor_data,
    create_search_cursor_data,
    encode_cursor_data,
)

ArticleRow = namedtuple(
    "ArticleRow",
    [
        "id",
        "title",
        "media_url",
        "published_at",
        "summary",
        "canonical_url",
        "author",
        "created_at",
    ],
)


@dataclass
class ArticleMetadata:
    """Metadata for an article from the query result."""

    subscription_id: UUID
    subscription_title: str
    subscription_website: str | None
    is_read: bool
    read_later: bool
    relevance: float | None = None


@dataclass
class ArticlesQueryResult:
    """Result from articles query execution."""

    articles: list[ArticleRow]
    metadata: dict[UUID, ArticleMetadata]
    next_cursor: str | None
    has_more: bool


class ArticleRepository:
    """Repository for article state management and query operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the article repository."""
        self.db = db

    async def get_user_article_state(
        self, article_id: UUID, current_user: User
    ) -> UserArticle:
        """Get user article state, raising NotFoundError if missing."""
        state_query = select(UserArticle).where(
            UserArticle.user_id == current_user.id,
            UserArticle.article_id == article_id,
        )
        state_result = await self.db.execute(state_query)
        state = state_result.scalar_one_or_none()

        if not state:
            raise NotFoundError(
                f"Article state not found for article {article_id} and user {current_user.id}. "
                "This indicates a data integrity issue - state records should exist for all accessible articles."
            )

        return state

    async def find_by_id(
        self, article_id: UUID, user_id: UUID
    ) -> UserArticle | None:
        """Get user article by ID with user filtering."""
        state_query = select(UserArticle).where(
            UserArticle.user_id == user_id,
            UserArticle.article_id == article_id,
        )
        state_result = await self.db.execute(state_query)
        return state_result.scalar_one_or_none()

    async def mark_article_as_read(
        self, article_id: UUID, current_user: User
    ) -> None:
        """Mark an article as read and update user's last_active timestamp."""
        state = await self.get_user_article_state(article_id, current_user)

        if not state.is_read:
            state.is_read = True
            state.read_at = func.now()

        current_user.last_active = func.now()

    async def update_article_read_state(
        self,
        article_id: UUID,
        state_update_data: dict[str, Any],
        current_user: User,
    ) -> bool:
        """Update article read state (is_read, read_later)."""
        if not state_update_data:
            return False

        state = await self.get_user_article_state(article_id, current_user)

        for field, value in state_update_data.items():
            setattr(state, field, value)

        if state_update_data.get("is_read") and not state.read_at:
            state.read_at = func.now()

        return True

    async def bulk_mark_articles(
        self,
        current_user: User,
        article_ids: list[UUID],
        is_read: bool,
    ) -> int:
        """Bulk mark articles as read or unread."""
        if not article_ids:
            return 0

        if is_read:
            condition = and_(
                UserArticle.user_id == current_user.id,
                UserArticle.article_id.in_(article_ids),
                UserArticle.is_read.is_(False),
            )
            values = {"is_read": True, "read_at": func.now()}
        else:
            condition = and_(
                UserArticle.user_id == current_user.id,
                UserArticle.article_id.in_(article_ids),
                UserArticle.is_read.is_(True),
            )
            values = {"is_read": False, "read_at": None}

        update_result = await self.db.execute(
            update(UserArticle).where(condition).values(**values)
        )
        return update_result.rowcount

    def build_articles_base_query(
        self,
        current_user: User,
        subscription_ids: list[UUID] | None = None,
        folder_ids: list[UUID] | None = None,
        tag_ids: list[UUID] | None = None,
        is_read: str | None = None,
        read_later: str | None = None,
        q: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Select[tuple[Any, ...]]:
        """Build base query for articles with filters applied."""
        has_search_query = q and q != "*"

        if has_search_query:
            ts_query = func.plainto_tsquery("english", q)
        else:
            ts_query = None

        # Subquery to select one UserFeed per Article, deduplicating articles
        # that appear in multiple feeds. Uses DISTINCT ON (article_id) which
        # requires ORDER BY to start with article_id.
        feed_subq = (
            select(
                ArticleSource.article_id,
                UserFeed.id.label("sub_id"),
                UserFeed.title.label("sub_title"),
                Feed.website.label("sub_website"),
                UserArticle.is_read.label("sub_is_read"),
                UserArticle.read_later.label("sub_read_later"),
            )
            .join(Feed, UserFeed.feed_id == Feed.id)
            .join(ArticleSource, Feed.id == ArticleSource.feed_id)
            .join(
                UserArticle, ArticleSource.article_id == UserArticle.article_id
            )
            .join(
                Article, ArticleSource.article_id == Article.id
            )  # Join Article for search filtering
            .where(
                and_(
                    UserArticle.user_id == current_user.id,
                    UserFeed.user_id == current_user.id,
                )
            )
        )

        # Apply search filter FIRST in the subquery (before DISTINCT ON)
        # This allows the GIN index to restrict rows early
        if has_search_query:
            feed_subq = feed_subq.where(
                or_(
                    Article.textsearchable.op("@@")(ts_query),
                    Article.title.op("%")(q),
                )
            )

        if subscription_ids:
            feed_subq = feed_subq.where(UserFeed.id.in_(subscription_ids))
        if folder_ids:
            feed_subq = feed_subq.where(UserFeed.folder_id.in_(folder_ids))
        if is_read is not None:
            feed_subq = feed_subq.where(
                UserArticle.is_read == (is_read == "read")
            )
        if read_later is not None:
            feed_subq = feed_subq.where(
                UserArticle.read_later == (read_later == "true")
            )

        feed_subq = (
            feed_subq.order_by(ArticleSource.article_id, UserFeed.id)
            .distinct(ArticleSource.article_id)
            .subquery()
        )

        if has_search_query:
            query = select(
                Article.id,
                Article.title,
                Article.media_url,
                Article.published_at,
                Article.summary,
                Article.canonical_url,
                Article.author,
                Article.created_at,
                feed_subq.c.sub_id.label("subscription_id"),
                feed_subq.c.sub_title.label("subscription_title"),
                feed_subq.c.sub_website.label("subscription_website"),
                feed_subq.c.sub_is_read.label("is_read"),
                feed_subq.c.sub_read_later.label("read_later"),
                ts_query.op("@@")(Article.textsearchable).label("text_match"),
                func.greatest(
                    func.ts_rank(Article.textsearchable, ts_query),
                    func.similarity(Article.title, q),
                ).label("relevance"),
            ).join(feed_subq, Article.id == feed_subq.c.article_id)
        else:
            query = select(
                Article.id,
                Article.title,
                Article.media_url,
                Article.published_at,
                Article.summary,
                Article.canonical_url,
                Article.author,
                Article.created_at,
                feed_subq.c.sub_id.label("subscription_id"),
                feed_subq.c.sub_title.label("subscription_title"),
                feed_subq.c.sub_website.label("subscription_website"),
                feed_subq.c.sub_is_read.label("is_read"),
                feed_subq.c.sub_read_later.label("read_later"),
                literal_column("1.0").label("relevance"),
            ).join(feed_subq, Article.id == feed_subq.c.article_id)

        if tag_ids:
            query = (
                query.join(UserArticle, Article.id == UserArticle.article_id)
                .join(ArticleTag, UserArticle.id == ArticleTag.user_article_id)
                .join(UserTag, ArticleTag.user_tag_id == UserTag.id)
                .where(
                    and_(
                        ArticleTag.user_tag_id.in_(tag_ids),
                        UserTag.user_id == current_user.id,
                    )
                )
            )

        if from_date:
            from_datetime = datetime.combine(from_date, time.min).replace(
                tzinfo=UTC
            )
            query = query.where(
                and_(
                    Article.published_at.isnot(None),
                    Article.published_at >= from_datetime,
                )
            )

        if to_date:
            to_datetime = datetime.combine(to_date, time.max).replace(
                tzinfo=UTC
            )
            query = query.where(
                and_(
                    Article.published_at.isnot(None),
                    Article.published_at <= to_datetime,
                )
            )

        # This makes the 'relevance' column available for ORDER BY and WHERE
        if has_search_query:
            query = query.subquery()
            query = select(query)  # type: ignore[call-overload]

        return query

    def build_cursor_filtering(
        self,
        base_query: Select[tuple[Any, ...]],
        cursor_data: dict[str, Any],
        has_search: bool = False,
        q: str | None = None,
    ) -> Select[tuple[Any, ...]]:
        """Apply cursor filtering to articles query."""
        from sqlalchemy import ClauseList

        if has_search and q:
            subq = base_query.froms[0]
            col_relevance = subq.c.relevance
            col_published_at = subq.c.published_at
            col_created_at = subq.c.created_at
            col_id = subq.c.id
        else:
            col_relevance = None
            col_published_at = Article.published_at
            col_created_at = Article.created_at
            col_id = Article.id

        if has_search and q and col_relevance is not None:
            order_clause: ClauseList = (
                col_relevance.desc(),
                nullslast(col_published_at.desc()),
                col_created_at.desc(),
                col_id.desc(),
            )
        else:
            order_clause = (
                nullslast(col_published_at.desc()),
                col_created_at.desc(),
                col_id.desc(),
            )

        if not cursor_data:
            return base_query.order_by(*order_clause)

        has_relevance = "relevance" in cursor_data

        if has_search and has_relevance and q and col_relevance is not None:
            cursor_relevance = float(cursor_data.get("relevance", 0))
            cursor_timestamp = datetime.fromisoformat(
                cursor_data["timestamp"].replace("Z", "+00:00")
            )
            cursor_timestamp_naive = cursor_timestamp.replace(tzinfo=None)
            is_published_at = cursor_data.get("is_published_at", True)
            article_id = cursor_data.get("article_id")

            cursor_conditions = [and_(col_relevance < cursor_relevance)]

            if is_published_at:
                if article_id:
                    cursor_conditions.append(
                        and_(
                            col_relevance == cursor_relevance,
                            or_(
                                and_(
                                    col_published_at.isnot(None),
                                    col_published_at < cursor_timestamp,
                                ),
                                and_(
                                    col_published_at.isnot(None),
                                    col_published_at == cursor_timestamp,
                                    col_id < article_id,
                                ),
                                col_published_at.is_(None),
                            ),
                        )
                    )
                else:
                    cursor_conditions.append(
                        and_(
                            col_relevance == cursor_relevance,
                            or_(
                                and_(
                                    col_published_at.isnot(None),
                                    col_published_at < cursor_timestamp,
                                ),
                                col_published_at.is_(None),
                            ),
                        )
                    )
            else:
                if article_id:
                    cursor_conditions.append(
                        and_(
                            col_relevance == cursor_relevance,
                            col_published_at.is_(None),
                            or_(
                                col_created_at < cursor_timestamp_naive,
                                and_(
                                    col_created_at == cursor_timestamp_naive,
                                    col_id < article_id,
                                ),
                            ),
                        )
                    )
                else:
                    cursor_conditions.append(
                        and_(
                            col_relevance == cursor_relevance,
                            col_published_at.is_(None),
                            col_created_at < cursor_timestamp_naive,
                        )
                    )

            base_query = base_query.where(or_(*cursor_conditions))
        else:
            cursor_timestamp = datetime.fromisoformat(
                cursor_data["timestamp"].replace("Z", "+00:00")
            )
            cursor_timestamp_naive = cursor_timestamp.replace(tzinfo=None)
            is_published_at = cursor_data.get("is_published_at", True)
            article_id = cursor_data.get("article_id")

            if is_published_at:
                if article_id:
                    base_query = base_query.where(
                        or_(
                            and_(
                                col_published_at.isnot(None),
                                col_published_at < cursor_timestamp,
                            ),
                            and_(
                                col_published_at.isnot(None),
                                col_published_at == cursor_timestamp,
                                col_id < article_id,
                            ),
                            col_published_at.is_(None),
                        )
                    )
                else:
                    base_query = base_query.where(
                        or_(
                            and_(
                                col_published_at.isnot(None),
                                col_published_at < cursor_timestamp,
                            ),
                            col_published_at.is_(None),
                        )
                    )
            else:
                if article_id:
                    base_query = base_query.where(
                        and_(
                            col_published_at.is_(None),
                            or_(
                                col_created_at < cursor_timestamp_naive,
                                and_(
                                    col_created_at == cursor_timestamp_naive,
                                    col_id < article_id,
                                ),
                            ),
                        )
                    )
                else:
                    base_query = base_query.where(
                        and_(
                            col_published_at.is_(None),
                            col_created_at < cursor_timestamp_naive,
                        )
                    )

        return base_query.order_by(*order_clause)

    async def execute_articles_query(
        self,
        query: Select[tuple[Any, ...]],
        limit: int,
        has_search: bool = False,
    ) -> ArticlesQueryResult:
        """Execute the articles query with cursor pagination."""
        query = query.limit(limit + 1)
        result = await self.db.execute(query)
        article_rows = result.all()

        has_more = len(article_rows) > limit
        if has_more:
            article_rows = article_rows[:-1]

        articles = []
        metadata: dict[UUID, ArticleMetadata] = {}

        for row in article_rows:
            article = ArticleRow(
                id=row[0],
                title=row[1],
                media_url=row[2],
                published_at=row[3],
                summary=row[4],
                canonical_url=row[5],
                author=row[6],
                created_at=row[7],
            )

            relevance = None
            if has_search and len(row) > 14:
                relevance = float(row[14]) if row[14] is not None else None

            articles.append(article)
            metadata[article.id] = ArticleMetadata(
                subscription_id=row[8],
                subscription_title=str(row[9]) if row[9] else "",
                subscription_website=row[10],
                is_read=bool(row[11]),
                read_later=bool(row[12]),
                relevance=relevance,
            )

        next_cursor = None
        if articles and has_more:
            last_article = articles[-1]
            last_metadata = metadata[last_article.id]

            if has_search and last_metadata.relevance is not None:
                cursor_data = create_search_cursor_data(
                    last_article.id,
                    last_article.published_at,
                    last_article.created_at,
                    last_metadata.relevance,
                )
            else:
                cursor_data = create_article_cursor_data(
                    last_article.id,
                    last_article.published_at,
                    last_article.created_at,
                )
            next_cursor = encode_cursor_data(cursor_data)

        return ArticlesQueryResult(
            articles=articles,
            metadata=metadata,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_articles_count(
        self,
        current_user: User,
        subscription_ids: list[UUID] | None = None,
        folder_ids: list[UUID] | None = None,
        tag_ids: list[UUID] | None = None,
        is_read: str | None = None,
        read_later: str | None = None,
        q: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> int:
        """Get total count of articles matching the criteria."""
        count_query = (
            select(func.count(distinct(Article.id)))
            .select_from(UserArticle)
            .join(
                ArticleSource,
                UserArticle.article_id == ArticleSource.article_id,
            )
            .join(Feed, ArticleSource.feed_id == Feed.id)
            .join(UserFeed, Feed.id == UserFeed.feed_id)
            .join(Article, UserArticle.article_id == Article.id)
            .where(
                and_(
                    UserArticle.user_id == current_user.id,
                    UserFeed.user_id == current_user.id,
                )
            )
        )

        if subscription_ids:
            count_query = count_query.where(UserFeed.id.in_(subscription_ids))
        if folder_ids:
            count_query = count_query.where(UserFeed.folder_id.in_(folder_ids))
        if tag_ids:
            count_query = (
                count_query.join(
                    ArticleTag, UserArticle.id == ArticleTag.user_article_id
                )
                .join(UserTag, ArticleTag.user_tag_id == UserTag.id)
                .where(
                    and_(
                        ArticleTag.user_tag_id.in_(tag_ids),
                        UserTag.user_id == current_user.id,
                    )
                )
            )
        if is_read is not None:
            is_read_bool = is_read == "read"
            count_query = count_query.where(UserArticle.is_read == is_read_bool)
        if read_later is not None:
            read_later_bool = read_later == "true"
            count_query = count_query.where(
                UserArticle.read_later == read_later_bool
            )

        if from_date:
            from_datetime = datetime.combine(from_date, time.min).replace(
                tzinfo=UTC
            )
            count_query = count_query.where(
                and_(
                    Article.published_at.isnot(None),
                    Article.published_at >= from_datetime,
                )
            )

        if to_date:
            to_datetime = datetime.combine(to_date, time.max).replace(
                tzinfo=UTC
            )
            count_query = count_query.where(
                and_(
                    Article.published_at.isnot(None),
                    Article.published_at <= to_datetime,
                )
            )

        # Search filter (without relevance scoring for count)
        if q and q != "*":
            ts_query = func.plainto_tsquery("english", q)
            count_query = count_query.where(
                or_(
                    Article.textsearchable.op("@@")(ts_query),
                    Article.title.op("%")(q),
                )
            )

        result = await self.db.execute(count_query)
        return int(result.scalar() or 0)

    async def get_article_by_id(
        self, article_id: UUID, current_user: User
    ) -> tuple[Article, UUID, str, str | None] | None:
        """Get a specific article by ID with access verification."""
        query = (
            select(
                Article,
                UserFeed.id.label("subscription_id"),
                UserFeed.title.label("subscription_title"),
                Feed.website.label("subscription_website"),
            )
            .join(
                UserArticle,
                and_(
                    Article.id == UserArticle.article_id,
                    UserArticle.user_id == current_user.id,
                ),
            )
            .join(ArticleSource, Article.id == ArticleSource.article_id)
            .join(Feed, ArticleSource.feed_id == Feed.id)
            .join(
                UserFeed,
                and_(
                    Feed.id == UserFeed.feed_id,
                    UserFeed.user_id == current_user.id,
                ),
            )
            .where(Article.id == article_id)
        )

        result = await self.db.execute(query)
        row = result.first()
        if row:
            return row[0], row[1], row[2], row[3]

        return None

    async def get_article_tags(
        self, article_ids: list[UUID], current_user: User
    ) -> dict[UUID, list[UserTag]]:
        """Get tags for multiple articles."""
        if not article_ids:
            return {}

        tags_by_article: dict[UUID, list[UserTag]] = {}

        user_articles_result = await self.db.execute(
            select(UserArticle.id, UserArticle.article_id).where(
                and_(
                    UserArticle.user_id == current_user.id,
                    UserArticle.article_id.in_(article_ids),
                )
            )
        )
        user_article_map = {
            row.article_id: row.id for row in user_articles_result.all()
        }

        if not user_article_map:
            return {}

        tags_result = await self.db.execute(
            select(UserTag, ArticleTag.user_article_id)
            .join(ArticleTag)
            .where(
                and_(
                    ArticleTag.user_article_id.in_(user_article_map.values()),
                    UserTag.user_id == current_user.id,
                )
            )
            .order_by(UserTag.name)
        )

        reverse_map = {v: k for k, v in user_article_map.items()}
        for tag, user_article_id in tags_result.all():
            article_id = reverse_map.get(user_article_id)
            if article_id:
                if article_id not in tags_by_article:
                    tags_by_article[article_id] = []
                tags_by_article[article_id].append(tag)

        return tags_by_article

    async def build_mark_all_articles_query(
        self,
        current_user: User,
        subscription_ids: list[UUID] | None = None,
        folder_ids: list[UUID] | None = None,
        tag_ids: list[UUID] | None = None,
        is_read_filter: str | None = None,
        read_later: str | None = None,
        q: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Select[tuple[UUID]]:
        """Build query for mark-all operations."""
        base_query = (
            select(Article.id)
            .join(UserArticle, Article.id == UserArticle.article_id)
            .join(ArticleSource, Article.id == ArticleSource.article_id)
            .join(Feed, ArticleSource.feed_id == Feed.id)
            .join(
                UserFeed,
                and_(
                    Feed.id == UserFeed.feed_id,
                    UserFeed.user_id == current_user.id,
                ),
            )
            .where(UserArticle.user_id == current_user.id)
            .distinct()
        )

        if subscription_ids:
            base_query = base_query.where(UserFeed.id.in_(subscription_ids))
        if folder_ids:
            base_query = base_query.where(UserFeed.folder_id.in_(folder_ids))
        if tag_ids:
            base_query = (
                base_query.join(
                    ArticleTag, UserArticle.id == ArticleTag.user_article_id
                )
                .join(UserTag, ArticleTag.user_tag_id == UserTag.id)
                .where(
                    and_(
                        ArticleTag.user_tag_id.in_(tag_ids),
                        UserTag.user_id == current_user.id,
                    )
                )
            )
        if is_read_filter is not None:
            is_read_bool = is_read_filter == "read"
            base_query = base_query.where(UserArticle.is_read == is_read_bool)
        if read_later is not None:
            read_later_bool = read_later == "true"
            base_query = base_query.where(
                UserArticle.read_later == read_later_bool
            )
        if from_date:
            from_datetime = datetime.combine(from_date, time.min).replace(
                tzinfo=UTC
            )
            base_query = base_query.where(
                and_(
                    Article.published_at.isnot(None),
                    Article.published_at >= from_datetime,
                )
            )
        if to_date:
            to_datetime = datetime.combine(to_date, time.max).replace(
                tzinfo=UTC
            )
            base_query = base_query.where(
                and_(
                    Article.published_at.isnot(None),
                    Article.published_at <= to_datetime,
                )
            )
        if q and q != "*":
            ts_query = func.plainto_tsquery("english", q)
            base_query = base_query.where(
                or_(
                    Article.textsearchable.op("@@")(ts_query),
                    Article.title.op("%")(q),
                )
            )

        return base_query

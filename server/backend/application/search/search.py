"""Search application service using Postgres full-text search.

Native Postgres search using tsvector and pg_trgm.
"""

import asyncio
from typing import Any, Literal, cast
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.repositories.search import SearchRepository
from backend.models import User
from backend.schemas.core.common import PaginationMetadata
from backend.schemas.domain import (
    ArticleListResponse,
    FeedSearchHit,
    FeedSearchRequest,
    FeedSearchResponse,
    FolderSearchHit,
    FolderSearchRequest,
    FolderSearchResponse,
    TagSearchHit,
    TagSearchRequest,
    TagSearchResponse,
    UnifiedSearchHit,
    UnifiedSearchRequest,
    UnifiedSearchResponse,
)

logger = structlog.get_logger()


class SearchApplication:
    """Application service for Postgres-based universal search.

    Provides methods for searching across articles, feeds, tags, and folders
    with full-text search and fuzzy matching.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the search application.

        Args:
            db: Database session.

        """
        self.db = db
        self.repository = SearchRepository(db)

    async def universal_search(
        self,
        request: UnifiedSearchRequest,
        current_user: User,
    ) -> UnifiedSearchResponse:
        """Execute union search across all content types.

        Searches all types and merges results with custom type weights.
        Returns up to 20 results total, ranked by relevance.

        Args:
            request: Universal search request with query.
            current_user: Authenticated user.

        Returns:
            Unified search response with up to 20 mixed, ranked results.

        """
        query = request.query

        type_weights = {
            "articles": 1.8,
            "feeds": 2.0,
            "tags": 0.8,
            "folders": 1.5,
        }

        per_type = 10

        search_tasks_with_types = [
            (
                "articles",
                self._search_articles_with_score(
                    query, current_user.id, per_type
                ),
            ),
            (
                "feeds",
                self._search_feeds_with_score(query, current_user.id, per_type),
            ),
            (
                "tags",
                self._search_tags_with_score(query, current_user.id, per_type),
            ),
            (
                "folders",
                self._search_folders_with_score(
                    query, current_user.id, per_type
                ),
            ),
        ]

        search_tasks = [task for _, task in search_tasks_with_types]
        search_types_ordered = [
            search_type for search_type, _ in search_tasks_with_types
        ]

        results_by_type = await asyncio.gather(
            *search_tasks, return_exceptions=True
        )

        for i, result in enumerate(results_by_type):
            if isinstance(result, Exception):
                logger.warning(
                    "Search type failed",
                    query=query,
                    search_type=search_types_ordered[i],
                    error=str(result),
                )

        weighted_hits: list[tuple[float, UnifiedSearchHit]] = []

        for search_type, result in zip(
            search_types_ordered, results_by_type, strict=True
        ):
            if isinstance(result, Exception):
                continue

            weight = type_weights[search_type]
            hit_type = search_type.rstrip("s")

            hits = cast(list[dict[str, Any]], result)
            for hit in hits:
                weighted_score = hit["score"] * weight
                weighted_hits.append(
                    (weighted_score, self._dict_to_unified_hit(hit, hit_type))
                )

        weighted_hits.sort(key=lambda x: x[0], reverse=True)
        top_hits = [hit for _, hit in weighted_hits[:20]]

        return UnifiedSearchResponse(data=top_hits)

    async def search_feeds(
        self,
        request: FeedSearchRequest,
        current_user: User,
    ) -> FeedSearchResponse:
        """Search feeds.

        Args:
            request: Feed search request.
            current_user: Authenticated user.

        Returns:
            Feed search response with hits and pagination.

        """
        raw_result = await self.repository.search_feeds(
            query=request.query,
            user_id=current_user.id,
            limit=request.limit,
            offset=request.offset,
        )

        hits = [FeedSearchHit(**hit) for hit in raw_result.get("data", [])]

        return FeedSearchResponse(
            data=hits,
            pagination=PaginationMetadata(
                total=raw_result.get("pagination", {}).get("total", 0),
                limit=request.limit,
                offset=request.offset,
                next_cursor=raw_result.get("pagination", {}).get("next_cursor"),
                has_more=raw_result.get("pagination", {}).get(
                    "has_more", False
                ),
            ),
        )

    async def search_tags(
        self,
        request: TagSearchRequest,
        current_user: User,
    ) -> TagSearchResponse:
        """Search tags.

        Args:
            request: Tag search request.
            current_user: Authenticated user.

        Returns:
            Tag search response with hits and pagination.

        """
        raw_result = await self.repository.search_tags(
            query=request.query,
            user_id=current_user.id,
            limit=request.limit,
            offset=request.offset,
        )

        hits = [TagSearchHit(**hit) for hit in raw_result.get("data", [])]

        return TagSearchResponse(
            data=hits,
            pagination=PaginationMetadata(
                total=raw_result.get("pagination", {}).get("total", 0),
                limit=request.limit,
                offset=request.offset,
                next_cursor=raw_result.get("pagination", {}).get("next_cursor"),
                has_more=raw_result.get("pagination", {}).get(
                    "has_more", False
                ),
            ),
        )

    async def search_folders(
        self,
        request: FolderSearchRequest,
        current_user: User,
    ) -> FolderSearchResponse:
        """Search folders.

        Args:
            request: Folder search request.
            current_user: Authenticated user.

        Returns:
            Folder search response with hits and pagination.

        """
        raw_result = await self.repository.search_folders(
            query=request.query,
            user_id=current_user.id,
            limit=request.limit,
            offset=request.offset,
        )

        hits = [FolderSearchHit(**hit) for hit in raw_result.get("data", [])]

        return FolderSearchResponse(
            data=hits,
            pagination=PaginationMetadata(
                total=raw_result.get("pagination", {}).get("total", 0),
                limit=request.limit,
                offset=request.offset,
                next_cursor=raw_result.get("pagination", {}).get("next_cursor"),
                has_more=raw_result.get("pagination", {}).get(
                    "has_more", False
                ),
            ),
        )

    async def _search_articles_with_score(
        self,
        query: str,
        user_id: UUID,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search articles and return hits with scores."""
        from backend.infrastructure.repositories.article import (
            ArticleRepository,
        )
        from backend.models import User

        mock_user = User(id=user_id)

        article_repo = ArticleRepository(self.db)

        base_query = article_repo.build_articles_base_query(mock_user, q=query)
        query_result = await article_repo.execute_articles_query(
            base_query, limit, has_search=True
        )

        hits_with_relevance = []
        for article in query_result.articles:
            metadata = query_result.metadata.get(article.id)
            if not metadata:
                continue

            article_dict = {
                "id": article.id,
                "title": article.title or "",
                "summary": article.summary,
                "published_at": article.published_at,
                "is_read": metadata.is_read,
                "read_later": metadata.read_later,
                "media_url": article.media_url,
                "feeds": [
                    {
                        "id": metadata.subscription_id,
                        "title": metadata.subscription_title,
                        "website": metadata.subscription_website or "",
                    }
                ],
            }
            relevance = (
                metadata.relevance if metadata.relevance is not None else 0.0
            )
            hits_with_relevance.append(
                {
                    **article_dict,
                    "_relevance": relevance,
                }
            )

        normalized = self._normalize_scores(hits_with_relevance)

        return [
            {
                "type": "articles",
                "score": hit["score"],
                "id": hit["id"],
                "title": hit["title"],
                "data": hit,
            }
            for hit in normalized
        ]

    async def _search_feeds_with_score(
        self,
        query: str,
        user_id: UUID,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search feeds and return hits with scores."""
        raw_result = await self.repository.search_feeds(
            query=query,
            user_id=user_id,
            limit=limit,
            offset=0,
        )

        hits = []
        for raw_hit in raw_result.get("data", []):
            relevance = raw_hit.get("_relevance", 0.0) / 1.5
            hits.append(
                {
                    "type": "feeds",
                    "score": max(0.0, min(1.0, relevance)),
                    "id": raw_hit["id"],
                    "title": raw_hit["title"],
                    "data": raw_hit,
                }
            )

        return hits

    async def _search_tags_with_score(
        self,
        query: str,
        user_id: UUID,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search tags and return hits with scores."""
        raw_result = await self.repository.search_tags(
            query=query,
            user_id=user_id,
            limit=limit,
            offset=0,
        )

        hits = []
        for raw_hit in raw_result.get("data", []):
            relevance = raw_hit.get("_relevance", 0.0) / 1.5
            hits.append(
                {
                    "type": "tags",
                    "score": max(0.0, min(1.0, relevance)),
                    "id": raw_hit["id"],
                    "title": raw_hit["name"],
                    "data": raw_hit,
                }
            )

        return hits

    async def _search_folders_with_score(
        self,
        query: str,
        user_id: UUID,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search folders and return hits with scores."""
        raw_result = await self.repository.search_folders(
            query=query,
            user_id=user_id,
            limit=limit,
            offset=0,
        )

        hits = []
        for raw_hit in raw_result.get("data", []):
            relevance = raw_hit.get("_relevance", 0.0) / 1.5
            hits.append(
                {
                    "type": "folders",
                    "score": max(0.0, min(1.0, relevance)),
                    "id": raw_hit["id"],
                    "title": raw_hit["name"],
                    "data": raw_hit,
                }
            )

        return hits

    def _dict_to_unified_hit(
        self, hit_dict: dict[str, Any], result_type: str
    ) -> UnifiedSearchHit:
        """Convert a dict result to UnifiedSearchHit.

        Args:
            hit_dict: Dictionary with 'data' key containing the hit data.
            result_type: Type of result ('article', 'feed', 'tag', 'folder').

        Returns:
            UnifiedSearchHit with type and data (no score, id, or title at top level).

        """
        data = hit_dict.get("data", {})

        if result_type == "article":
            typed_data: (
                ArticleListResponse
                | FeedSearchHit
                | TagSearchHit
                | FolderSearchHit
            ) = ArticleListResponse(**data)
        elif result_type == "feed":
            typed_data = FeedSearchHit(**data)
        elif result_type == "tag":
            typed_data = TagSearchHit(**data)
        elif result_type == "folder":
            typed_data = FolderSearchHit(**data)
        else:
            typed_data = ArticleListResponse(**data)

        hit_type: Literal["article", "feed", "tag", "folder"] = cast(
            Literal["article", "feed", "tag", "folder"], result_type
        )

        return UnifiedSearchHit(
            type=hit_type,
            data=typed_data,
        )

    def _normalize_scores(
        self, hits: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Normalize relevance scores to 0-1 range using min-max normalization.

        Args:
            hits: List of hits with '_relevance' field.

        Returns:
            List of hits with normalized 'score' field (0-1 range).

        """
        if not hits:
            return []

        relevances = [hit.get("_relevance", 0.0) for hit in hits]
        max_rel = max(relevances)
        min_rel = min(relevances)
        range_rel = max_rel - min_rel

        if len(hits) == 1 or range_rel == 0:
            return [
                {**hit, "score": max(0.0, min(1.0, hit.get("_relevance", 0.0)))}
                for hit in hits
            ]

        return [
            {
                **hit,
                "score": max(
                    0.0,
                    min(
                        1.0, (hit.get("_relevance", 0.0) - min_rel) / range_rel
                    ),
                ),
            }
            for hit in hits
        ]

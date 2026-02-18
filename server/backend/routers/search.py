"""Universal search endpoints using Postgres full-text search."""

from fastapi import APIRouter, Depends, Query

from backend.application.search.search import SearchApplication
from backend.core.dependencies import get_search_application
from backend.core.fastapi import get_user_from_request_state
from backend.models import User
from backend.schemas.domain import (
    FeedSearchRequest,
    FeedSearchResponse,
    FolderSearchRequest,
    FolderSearchResponse,
    TagSearchRequest,
    TagSearchResponse,
    UnifiedSearchRequest,
    UnifiedSearchResponse,
)

router = APIRouter()


@router.get(
    "",
    response_model=UnifiedSearchResponse,
    summary="Universal search",
    description="Search across articles, feeds, tags, and folders with intelligent ranking. Returns up to 20 results.",
    tags=["Search"],
)
async def universal_search(
    q: str = Query(
        ...,
        min_length=1,
        max_length=128,
        description="Search query string",
    ),
    search_app: SearchApplication = Depends(get_search_application),
    current_user: User = Depends(get_user_from_request_state),
) -> UnifiedSearchResponse:
    """Search across all content types with relevance ranking."""
    request = UnifiedSearchRequest(query=q)
    return await search_app.universal_search(request, current_user)


@router.get(
    "/feeds",
    response_model=FeedSearchResponse,
    summary="Search feeds",
    description="Search across user's feed subscriptions.",
    tags=["Search"],
)
async def search_feeds(
    q: str = Query(
        ...,
        min_length=1,
        max_length=128,
        description="Search query string",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Result offset for pagination",
    ),
    search_app: SearchApplication = Depends(get_search_application),
    current_user: User = Depends(get_user_from_request_state),
) -> FeedSearchResponse:
    """Search user's feed subscriptions."""
    request = FeedSearchRequest(
        query=q,
        limit=limit,
        offset=offset,
    )
    return await search_app.search_feeds(request, current_user)


@router.get(
    "/tags",
    response_model=TagSearchResponse,
    summary="Search tags",
    description="Search across user's tags.",
    tags=["Search"],
)
async def search_tags(
    q: str = Query(
        ...,
        min_length=1,
        max_length=128,
        description="Search query string",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=50,
        description="Maximum number of results",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Result offset for pagination",
    ),
    search_app: SearchApplication = Depends(get_search_application),
    current_user: User = Depends(get_user_from_request_state),
) -> TagSearchResponse:
    """Search user's tags."""
    request = TagSearchRequest(
        query=q,
        limit=limit,
        offset=offset,
    )
    return await search_app.search_tags(request, current_user)


@router.get(
    "/folders",
    response_model=FolderSearchResponse,
    summary="Search folders",
    description="Search across user's folders.",
    tags=["Search"],
)
async def search_folders(
    q: str = Query(
        ...,
        min_length=1,
        max_length=128,
        description="Search query string",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=50,
        description="Maximum number of results",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Result offset for pagination",
    ),
    search_app: SearchApplication = Depends(get_search_application),
    current_user: User = Depends(get_user_from_request_state),
) -> FolderSearchResponse:
    """Search user's folders."""
    request = FolderSearchRequest(
        query=q,
        limit=limit,
        offset=offset,
    )
    return await search_app.search_folders(request, current_user)

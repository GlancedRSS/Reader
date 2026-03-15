from fastapi import APIRouter, Depends

from backend.core.dependencies import get_discovery_application
from backend.core.fastapi import get_user_from_request_state
from backend.models import User
from backend.schemas.domain import (
    FeedDiscoveryRequest,
    FeedDiscoveryResponse,
)
from backend.utils.validators import validate_url

router = APIRouter()


@router.post(
    "",
    response_model=FeedDiscoveryResponse,
    summary="Discover feeds",
    description="Subscribe to RSS/Atom feeds from a URL.",
    tags=["Discovery"],
)
async def discover_feeds(
    request: FeedDiscoveryRequest,
    discovery_app=Depends(get_discovery_application),
    current_user: User = Depends(get_user_from_request_state),
) -> FeedDiscoveryResponse:
    validate_url(request.url)
    return await discovery_app.discover_feeds(
        request.url, current_user.id, request.folder_id
    )

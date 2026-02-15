"""Data access repositories for all domain entities."""

from backend.infrastructure.repositories.article import (
    ArticleRepository,
    ArticlesQueryResult,
)
from backend.infrastructure.repositories.feed import FeedRepository
from backend.infrastructure.repositories.folder import FolderRepository
from backend.infrastructure.repositories.opml import OpmlRepository
from backend.infrastructure.repositories.session import SessionRepository
from backend.infrastructure.repositories.subscription import (
    SubscriptionRepository,
)
from backend.infrastructure.repositories.tag import UserTagRepository
from backend.infrastructure.repositories.user import UserRepository
from backend.infrastructure.repositories.user_feed import (
    UserFeedRepository,
    UserFeedsQueryResult,
)

__all__ = [
    "ArticleRepository",
    "ArticlesQueryResult",
    "FeedRepository",
    "FolderRepository",
    "OpmlRepository",
    "SessionRepository",
    "SubscriptionRepository",
    "UserFeedRepository",
    "UserFeedsQueryResult",
    "UserRepository",
    "UserTagRepository",
]

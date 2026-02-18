"""Dependency injection for FastAPI services."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.article import ArticleApplication
from backend.application.discovery import DiscoveryApplication
from backend.application.feed import FeedApplication
from backend.application.folder import FolderApplication
from backend.application.notification import NotificationApplication
from backend.application.opml import OpmlApplication
from backend.application.search.search import SearchApplication
from backend.application.tag import TagApplication
from backend.application.user import UserPreferencesApplication
from backend.core.database import get_db
from backend.infrastructure.publishers import DiscoveryPublisher


async def get_discovery_publisher() -> AsyncGenerator[DiscoveryPublisher]:
    """Yield a DiscoveryPublisher instance."""
    yield DiscoveryPublisher()


async def get_feed_application(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[FeedApplication]:
    """Yield a FeedApplication instance."""
    yield FeedApplication(db)


async def get_discovery_application(
    db: AsyncSession = Depends(get_db),
    discovery_publisher: DiscoveryPublisher = Depends(get_discovery_publisher),
    feed_application: FeedApplication = Depends(get_feed_application),
) -> AsyncGenerator[DiscoveryApplication]:
    """Yield a DiscoveryApplication instance."""
    yield DiscoveryApplication(
        db,
        discovery_publisher=discovery_publisher,
        feed_application=feed_application,
    )


async def get_article_application(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ArticleApplication]:
    """Yield an ArticleApplication instance."""
    yield ArticleApplication(db)


async def get_folder_application(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[FolderApplication]:
    """Yield a FolderApplication instance."""
    yield FolderApplication(db)


async def get_tag_application(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[TagApplication]:
    """Yield a TagApplication instance."""
    yield TagApplication(db)


async def get_user_preferences_application(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[UserPreferencesApplication]:
    """Yield a UserPreferencesApplication instance."""
    yield UserPreferencesApplication(db)


async def get_opml_application(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[OpmlApplication]:
    """Yield an OpmlApplication instance."""
    yield OpmlApplication(db)


async def get_notification_application() -> AsyncGenerator[
    NotificationApplication
]:
    """Yield a NotificationApplication instance."""
    yield NotificationApplication()


async def get_search_application(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[SearchApplication]:
    """Yield a SearchApplication instance."""
    yield SearchApplication(db)

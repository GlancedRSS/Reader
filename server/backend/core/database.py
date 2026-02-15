"""Database connection and session management for PostgreSQL."""

import urllib.parse
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from .app import settings


def get_database_url() -> str:
    """Get the database URL with asyncpg driver and sanitized query parameters.

    Converts postgresql:// to postgresql+asyncpg:// and removes unnecessary
    query parameters like channel_binding and application_name.

    Returns:
        The formatted database URL for asyncpg.

    """
    url = settings.database_url

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")

    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)

    for param in ["channel_binding", "application_name", "sslmode"]:
        query_params.pop(param, None)

    return urllib.parse.urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urllib.parse.urlencode(query_params, doseq=True),
            parsed.fragment,
        )
    )


engine = create_async_engine(
    get_database_url(),
    echo=settings.environment == "development",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "application_name": "glanced_backend",
            "search_path": "public, accounts, content, personalization, extensions",
        }
    },
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Yield a database session with automatic commit/rollback/close.

    Provides a dependency-injectable database session for FastAPI endpoints.
    Commits on success, rolls back on exception, and always closes.

    Yields:
        An async SQLAlchemy session.

    Raises:
        Exception: Any exception from the caller is re-raised after rollback.

    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database connection, create extensions, and create tables.

    Tests the database connection and creates all tables defined in SQLAlchemy models.

    Raises:
        Exception: If database initialization fails.

    """
    import structlog

    logger = structlog.get_logger()

    try:
        async with engine.begin() as conn:
            logger.info("Initializing database... [1/2] Testing connection")
            await conn.execute(text("SELECT 1"))

            logger.info("Creating database tables [2/2]")
            await conn.run_sync(Base.metadata.create_all)

            result = await conn.execute(
                text(
                    """
                SELECT COUNT(*) as table_count
                FROM information_schema.tables
                WHERE table_schema IN ('accounts', 'content', 'personalization', 'management', 'extensions', 'public')
            """
                )
            )
            table_count = result.scalar()
            logger.info("Database ready", table_count=table_count)

    except Exception as e:
        logger.exception(
            "Database initialization failed", error_type=type(e).__name__
        )
        raise


async def check_database_health() -> tuple[bool, str]:
    """Check database connectivity and table availability.

    Tests basic connectivity and verifies that expected tables exist
    in the target schemas.

    Returns:
        A tuple of (is_healthy: bool, message: str).

    """
    import structlog

    logger = structlog.get_logger()

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() != 1:
                return False, "Database query failed"

            result = await conn.execute(
                text(
                    """
                SELECT COUNT(*) as table_count
                FROM information_schema.tables
                WHERE table_schema IN ('accounts', 'content', 'personalization', 'management', 'extensions', 'public')
            """
                )
            )
            table_count = result.scalar()
            if table_count == 0:
                return False, "No tables found in database"

            return True, f"Database healthy ({table_count} tables)"

    except Exception as e:
        logger.exception(
            "Database health check failed", error_type=type(e).__name__
        )
        return False, f"Database connection failed: {e!s}"

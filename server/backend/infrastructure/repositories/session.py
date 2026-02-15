"""Session data access layer for user session management."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.app import settings
from backend.infrastructure.auth.security import hash_token
from backend.models import User, UserSession

logger = structlog.get_logger()


def _extract_session_id(session_token: str) -> str | None:
    """Extract session ID from session token.

    Args:
        session_token: The session token containing the ID.

    Returns:
        The session ID, or None if extraction fails.

    """
    try:
        return session_token.split(".")[0]
    except (IndexError, AttributeError):
        return None


async def create_user_session_with_cookie(
    user_id: UUID,
    session_id: UUID,
    db: AsyncSession,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[UserSession, str]:
    """Create a new user session with cookie token.

    Args:
        user_id: The user ID to create a session for.
        session_id: The unique session ID.
        db: The database session.
        user_agent: The user agent string (optional).
        ip_address: The client IP address (optional).

    Returns:
        Tuple of (UserSession, session_token).

    """
    secret_token = secrets.token_urlsafe(32)
    session_token = f"{session_id}.{secret_token}"
    cookie_hash = hash_token(session_token)

    expires_at = datetime.now(UTC) + timedelta(
        seconds=settings.session_cookie_max_age
    )

    session = UserSession(
        user_id=user_id,
        session_id=session_id,
        cookie_hash=cookie_hash,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    db.add(session)
    return session, session_token


async def verify_session_cookie(
    session_token: str, db: AsyncSession
) -> UserSession | None:
    """Verify a session cookie and return the session.

    Args:
        session_token: The session token to verify.
        db: The database session.

    Returns:
        The UserSession if valid, None otherwise.

    """
    if not session_token:
        return None

    session_id = _extract_session_id(session_token)
    if not session_id:
        return None

    try:
        stmt = select(UserSession).where(
            UserSession.session_id == session_id,
            UserSession.expires_at > datetime.now(UTC),
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            return None

        if not session.cookie_hash or session.cookie_hash != hash_token(
            session_token
        ):
            return None

        session.last_used = datetime.now(UTC)
        await db.flush()
        return session

    except Exception as e:
        logger.exception("Error verifying session cookie", error=str(e))
        return None


async def revoke_session_cookie(session_token: str, db: AsyncSession) -> bool:
    """Revoke a session cookie.

    Args:
        session_token: The session token to revoke.
        db: The database session.

    Returns:
        True if session was revoked, False otherwise.

    """
    if not session_token:
        return False

    session_id = _extract_session_id(session_token)
    if not session_id:
        return False

    try:
        stmt = select(UserSession).where(UserSession.session_id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            return False

        if not session.cookie_hash or session.cookie_hash != hash_token(
            session_token
        ):
            return False

        await db.delete(session)
        return True

    except Exception as e:
        logger.exception("Error revoking session cookie", error=str(e))
        return False


async def get_current_user_from_cookie(
    session_token: str, db: AsyncSession
) -> User | None:
    """Get current user from session cookie.

    Args:
        session_token: The session token to verify.
        db: The database session.

    Returns:
        The User if session is valid and user is active, None otherwise.

    """
    try:
        session = await verify_session_cookie(session_token, db)
        if not session:
            return None

        stmt = select(User).where(User.id == session.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        return user

    except Exception as e:
        logger.exception("Error getting current user from cookie", error=str(e))
        return None


class SessionRepository:
    """Data access layer for session operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the session repository.

        Args:
            db: Async database session.

        """
        self.db = db

    async def get_active_session_count(self, user_id: UUID) -> int:
        """Get count of active sessions for a user.

        Args:
            user_id: The user ID to count sessions for.

        Returns:
            Number of active (non-expired) sessions.

        """
        session_count_query = select(func.count(UserSession.session_id)).where(
            UserSession.user_id == user_id,
            UserSession.expires_at > datetime.now(UTC),
        )
        count_result = await self.db.execute(session_count_query)
        return count_result.scalar() or 0

    async def get_oldest_session(self, user_id: UUID) -> UserSession | None:
        """Get the oldest active session for a user.

        Args:
            user_id: The user ID to get the oldest session for.

        Returns:
            The oldest UserSession, or None if no active sessions exist.

        """
        oldest_session_query = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.expires_at > datetime.now(UTC),
            )
            .order_by(UserSession.last_used.asc())
            .limit(1)
        )

        oldest_result = await self.db.execute(oldest_session_query)
        return oldest_result.scalar_one_or_none()

    async def create_session(
        self, user_id: UUID, user_agent: str | None, ip_address: str | None
    ) -> tuple[UserSession, str]:
        """Create a new user session and return session info with token.

        Args:
            user_id: The user ID to create a session for.
            user_agent: The user agent string (optional).
            ip_address: The client IP address (optional).

        Returns:
            Tuple of (UserSession, session_token).

        """
        session_id = uuid.uuid4()
        session, session_token = await create_user_session_with_cookie(
            user_id=user_id,
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address,
            db=self.db,
        )
        return session, session_token

    async def revoke_all_user_sessions(self, user_id: UUID) -> int:
        """Revoke all sessions for a user.

        Args:
            user_id: The user ID to revoke sessions for.

        Returns:
            Number of sessions revoked.

        """
        stmt = delete(UserSession).where(UserSession.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.rowcount or 0

    async def revoke_session_by_id(
        self, user_id: UUID, session_id: UUID
    ) -> int:
        """Revoke a specific session by ID.

        Args:
            user_id: The user ID who owns the session.
            session_id: The session ID to revoke.

        Returns:
            Number of sessions revoked (0 or 1).

        """
        delete_stmt = delete(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.session_id == session_id,
        )

        result = await self.db.execute(delete_stmt)
        return result.rowcount or 0

    async def revoke_oldest_session(self, user_id: UUID) -> bool:
        """Revoke the oldest active session for a user.

        Args:
            user_id: The user ID to revoke the oldest session for.

        Returns:
            True if a session was revoked, False otherwise.

        """
        oldest = await self.get_oldest_session(user_id)
        if not oldest:
            return False

        delete_stmt = delete(UserSession).where(
            UserSession.session_id == oldest.session_id
        )

        result = await self.db.execute(delete_stmt)
        return (result.rowcount or 0) > 0

    async def get_user_sessions(self, user_id: UUID) -> list[UserSession]:
        """Get all active sessions for a user.

        Args:
            user_id: The user ID to get sessions for.

        Returns:
            List of active UserSessions.

        """
        stmt = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.expires_at > datetime.now(UTC),
            )
            .order_by(UserSession.last_used.desc())
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

"""Authentication utilities for FastAPI integration."""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User

from .database import get_db


async def get_user_from_request_state(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Get the authenticated user from the request state.

    Extracts the user ID from the request state (set by auth middleware)
    and fetches the corresponding active user from the database.

    Args:
        request: The FastAPI request object containing state.
        db: The database session (injected via dependency).

    Returns:
        The authenticated User object.

    Raises:
        HTTPException: If user_id is not in request state (401).
        HTTPException: If user is not found or inactive (401).

    """
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return user

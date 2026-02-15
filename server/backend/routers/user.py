"""User profile and preferences management endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.app import settings
from backend.core.database import get_db
from backend.core.dependencies import get_user_preferences_application
from backend.core.fastapi import get_user_from_request_state
from backend.models import User
from backend.schemas.core import ResponseMessage
from backend.schemas.domain import (
    PreferencesResponse,
    PreferencesUpdateRequest,
    ProfileUpdateRequest,
    UserResponse,
)

router = APIRouter()


@router.get(
    "/version",
    summary="Get API version",
    description="Retrieve the current API version.",
    tags=["User"],
)
async def get_version() -> dict[str, str]:
    """Retrieve the current API version."""
    return {"version": settings.version}


@router.get(
    "",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve the authenticated user's profile.",
    tags=["User"],
)
async def get_me(
    current_user: User = Depends(get_user_from_request_state),
) -> UserResponse:
    """Retrieve the authenticated user's profile."""
    return UserResponse(
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.put(
    "",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update the authenticated user's profile (first_name, last_name).",
    tags=["User"],
)
async def update_profile(
    profile_update: ProfileUpdateRequest,
    current_user: User = Depends(get_user_from_request_state),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update the authenticated user's profile."""
    update_data = profile_update.model_dump(exclude_unset=True)

    if update_data:
        for field, value in update_data.items():
            setattr(current_user, field, value)

        await db.commit()
        await db.refresh(current_user)

    return UserResponse(
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.get(
    "/preferences",
    response_model=PreferencesResponse,
    summary="Get user preferences",
    description="Retrieve all current user preferences.",
    tags=["User"],
)
async def get_user_preferences(
    current_user: User = Depends(get_user_from_request_state),
    user_preferences_app=Depends(get_user_preferences_application),
) -> PreferencesResponse:
    """Retrieve all current user preferences."""
    return await user_preferences_app.get_user_preferences(current_user)


@router.put(
    "/preferences",
    response_model=ResponseMessage,
    summary="Update user preferences",
    description="Update user preferences with partial validation.",
    tags=["User"],
)
async def update_user_preferences(
    preferences_update: PreferencesUpdateRequest,
    current_user: User = Depends(get_user_from_request_state),
    user_preferences_app=Depends(get_user_preferences_application),
) -> ResponseMessage:
    """Update user preferences with partial validation."""
    return await user_preferences_app.update_user_preferences(
        current_user,
        preferences_update,
    )

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User
from backend.models import (
    UserPreferences as UserPreferencesModel,
)

_USER_PROTECTED_FIELDS = {"id", "created_at", "updated_at"}
_PREFERENCES_PROTECTED_FIELDS = {"user_id", "created_at"}


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def username_exists(self, username: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None

    async def find_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def count_users(self) -> int:
        result = await self.db.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def create_user(
        self,
        username: str,
        password_hash: str,
        first_name: str | None = None,
        last_name: str | None = None,
        is_admin: bool = False,
    ) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def update_user(
        self, user: User, update_data: dict[str, Any]
    ) -> User:
        for field, value in update_data.items():
            if field in _USER_PROTECTED_FIELDS:
                continue
            if hasattr(user, field):
                setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def find_preferences_by_user_id(
        self, user_id: UUID
    ) -> UserPreferencesModel | None:
        query = select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_preferences(
        self, user: User, **fields: Any
    ) -> UserPreferencesModel:
        prefs_model = UserPreferencesModel(user_id=user.id, **fields)
        self.db.add(prefs_model)
        await self.db.flush()
        await self.db.refresh(prefs_model)
        return prefs_model

    async def update_preferences(
        self, prefs_model: UserPreferencesModel, update_data: dict[str, Any]
    ) -> UserPreferencesModel:
        for field, value in update_data.items():
            if field in _PREFERENCES_PROTECTED_FIELDS:
                continue
            if hasattr(prefs_model, field):
                setattr(prefs_model, field, value)

        await self.db.flush()
        await self.db.refresh(prefs_model)
        return prefs_model

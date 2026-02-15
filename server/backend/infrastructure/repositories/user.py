"""User data access layer for user CRUD and preferences operations."""

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
    """Repository for user and preferences database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the user repository.

        Args:
            db: Async database session.

        """
        self.db = db

    async def username_exists(self, username: str) -> bool:
        """Check if a username already exists.

        Args:
            username: The username to check for existence.

        Returns:
            True if username exists, False otherwise.

        """
        result = await self.db.execute(
            select(User.id).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None

    async def find_by_username(self, username: str) -> User | None:
        """Find a user by username.

        Args:
            username: The username to search for.

        Returns:
            The User if found, None otherwise.

        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def count_users(self) -> int:
        """Count total number of users.

        Returns:
            Total user count.

        """
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
        """Create a new user.

        Args:
            username: The username (for cookie authentication).
            password_hash: Hashed password (for cookie authentication).
            first_name: User's first name (optional).
            last_name: User's last name (optional).
            is_admin: Whether user is an admin.

        Returns:
            The created User object.

        """
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
        """Update user fields.

        Args:
            user: The User object to update.
            update_data: Dictionary of field names and values to update.

        Returns:
            The updated User object.

        """
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
        """Find user preferences by user ID.

        Args:
            user_id: The UUID of the user.

        Returns:
            The UserPreferencesModel if found, None otherwise.

        """
        query = select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_preferences(
        self, user: User, **fields: Any
    ) -> UserPreferencesModel:
        """Create user preferences with default or provided values.

        Args:
            user: The User object to associate preferences with.
            **fields: Arbitrary keyword arguments for preference fields.

        Returns:
            The created UserPreferencesModel object.

        """
        prefs_model = UserPreferencesModel(user_id=user.id, **fields)
        self.db.add(prefs_model)
        await self.db.flush()
        await self.db.refresh(prefs_model)
        return prefs_model

    async def update_preferences(
        self, prefs_model: UserPreferencesModel, update_data: dict[str, Any]
    ) -> UserPreferencesModel:
        """Update user preferences fields.

        Args:
            prefs_model: The UserPreferencesModel object to update.
            update_data: Dictionary of field names and values to update.

        Returns:
            The updated UserPreferencesModel object.

        """
        for field, value in update_data.items():
            if field in _PREFERENCES_PROTECTED_FIELDS:
                continue
            if hasattr(prefs_model, field):
                setattr(prefs_model, field, value)

        await self.db.flush()
        await self.db.refresh(prefs_model)
        return prefs_model

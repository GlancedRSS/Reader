"""Application service for user preferences operations."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import ValidationError
from backend.domain import UserPreferenceConfig
from backend.infrastructure.repositories import UserRepository
from backend.models import User
from backend.models import UserPreferences as UserPreferencesModel
from backend.schemas.core import ResponseMessage
from backend.schemas.domain import PreferencesUpdateRequest


class UserPreferencesApplication:
    """Application service for user preferences operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the user preferences application with database session.

        Args:
            db: Async database session for repository operations.

        """
        self.db = db
        self.repository = UserRepository(db)

    async def _ensure_preferences_exist(
        self, user: User
    ) -> UserPreferencesModel:
        """Ensure user preferences exist, creating defaults if needed.

        Args:
            user: The user to ensure preferences for.

        Returns:
            The UserPreferencesModel, either existing or newly created.

        """
        prefs_model = await self.repository.find_preferences_by_user_id(user.id)

        if not prefs_model:
            default_data = UserPreferenceConfig.get_defaults()
            try:
                prefs_model = await self.repository.create_preferences(
                    user, **default_data
                )
            except IntegrityError:
                prefs_model = await self.repository.find_preferences_by_user_id(
                    user.id
                )
                if not prefs_model:
                    raise

        return prefs_model

    async def get_user_preferences(self, user: User) -> UserPreferencesModel:
        """Get user preferences, creating defaults if needed.

        Args:
            user: The user to get preferences for.

        Returns:
            UserPreferencesModel with preferences.

        """
        return await self._ensure_preferences_exist(user)

    async def update_user_preferences(
        self, user: User, preferences_update: PreferencesUpdateRequest
    ) -> ResponseMessage:
        """Update user preferences with validation.

        Args:
            user: The user to update preferences for.
            preferences_update: The preferences update request.

        Returns:
            Response message indicating successful update.

        Raises:
            ValidationError: If preference validation fails or no fields provided.

        """
        prefs_model = await self._ensure_preferences_exist(user)

        update_data = preferences_update.model_dump(exclude_unset=True)

        if not update_data:
            raise ValidationError(
                "At least one preference field must be provided"
            )

        current_data = {
            field_name: getattr(prefs_model, field_name)
            for field_name in UserPreferenceConfig.FIELDS
            if hasattr(prefs_model, field_name)
        }

        merged_data = {**current_data, **update_data}

        try:
            validated_data = UserPreferenceConfig.validate_preferences(
                merged_data
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e

        await self.repository.update_preferences(prefs_model, validated_data)

        return ResponseMessage(message="User preferences updated successfully")

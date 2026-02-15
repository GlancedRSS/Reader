"""Unit tests for UserPreferencesApplication."""

import pytest

from backend.application.user import UserPreferencesApplication
from backend.core.exceptions import ValidationError
from backend.domain import UserPreferenceConfig
from backend.schemas.domain import PreferencesUpdateRequest


class TestUserPreferencesApplication:
    """Test UserPreferencesApplication class."""

    async def test_get_user_preferences_creates_defaults_when_not_exist(
        self, db_session
    ):
        """Should create default preferences when they don't exist."""
        from uuid import uuid4

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"new_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        app = UserPreferencesApplication(db_session)
        prefs = await app.get_user_preferences(user)

        assert prefs.user_id == user.id
        # Verify defaults
        assert prefs.theme == UserPreferenceConfig.FIELDS["theme"].default
        assert prefs.show_article_thumbnails is True
        assert prefs.font_size == "m"

    async def test_get_user_preferences_returns_existing(self, db_session):
        """Should return existing preferences without modifying."""
        from uuid import uuid4

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"exist_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )

        # First call creates default preferences
        app = UserPreferencesApplication(db_session)
        prefs1 = await app.get_user_preferences(user)

        # Verify defaults were created
        assert prefs1.user_id == user.id
        assert prefs1.theme == UserPreferenceConfig.FIELDS["theme"].default

        # Manually update to test returning existing preferences
        prefs1.theme = "dark"
        prefs1.font_size = "xl"
        prefs1.show_article_thumbnails = False
        await db_session.commit()

        # Second call should return the same preferences without modifying
        prefs2 = await app.get_user_preferences(user)

        assert prefs2.user_id == prefs1.user_id
        assert prefs2.theme == "dark"
        assert prefs2.font_size == "xl"
        assert prefs2.show_article_thumbnails is False

    async def test_update_user_preferences_with_valid_data(self, db_session):
        """Should update preferences with valid data."""
        from uuid import uuid4

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"upd_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        # Create initial preferences via app
        app = UserPreferencesApplication(db_session)
        initial_prefs = await app.get_user_preferences(user)
        initial_prefs.theme = "light"
        await db_session.commit()

        request = PreferencesUpdateRequest(theme="dark", font_size="l")

        result = await app.update_user_preferences(user, request)

        assert result.message == "User preferences updated successfully"

        # Verify changes
        prefs = await app.get_user_preferences(user)
        assert prefs.theme == "dark"
        assert prefs.font_size == "l"

    async def test_update_user_preferences_with_partial_update(
        self, db_session
    ):
        """Should update only specified fields, leaving others unchanged."""
        from uuid import uuid4

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"part_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        # Create initial preferences via app
        app = UserPreferencesApplication(db_session)
        initial_prefs = await app.get_user_preferences(user)
        initial_prefs.theme = "light"
        initial_prefs.font_size = "m"
        initial_prefs.show_article_thumbnails = True
        await db_session.commit()

        request = PreferencesUpdateRequest(theme="dark")

        await app.update_user_preferences(user, request)

        prefs = await app.get_user_preferences(user)
        assert prefs.theme == "dark"  # Changed
        assert prefs.font_size == "m"  # Unchanged
        assert prefs.show_article_thumbnails is True  # Unchanged

    async def test_update_user_preferences_raises_for_empty_update(
        self, db_session
    ):
        """Should raise ValidationError when no fields provided."""
        from uuid import uuid4

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"empty_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        # Create initial preferences via app
        app = UserPreferencesApplication(db_session)
        await app.get_user_preferences(user)

        request = PreferencesUpdateRequest()  # No fields set

        with pytest.raises(
            ValidationError, match="At least one preference field"
        ):
            await app.update_user_preferences(user, request)

    async def test_update_user_preferences_raises_for_invalid_choice(
        self, db_session
    ):
        """Should raise ValidationError for invalid choice value."""
        from uuid import uuid4

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"inv_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        # Create initial preferences via app
        app = UserPreferencesApplication(db_session)
        await app.get_user_preferences(user)

        request = PreferencesUpdateRequest(theme="invalid_theme")

        with pytest.raises(ValidationError, match="must be one of"):
            await app.update_user_preferences(user, request)

    async def test_update_user_preferences_raises_for_invalid_type(
        self, db_session
    ):
        """Should raise ValidationError for wrong type."""
        from uuid import uuid4

        from pydantic import ValidationError as PydanticValidationError

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"type_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        # Create initial preferences via app
        app = UserPreferencesApplication(db_session)
        await app.get_user_preferences(user)

        # Pydantic validates input before it reaches the application layer
        with pytest.raises(PydanticValidationError):
            PreferencesUpdateRequest(show_article_thumbnails="not_a_bool")

    async def test_update_user_preferences_creates_defaults_if_missing(
        self, db_session
    ):
        """Should create default preferences before updating if they don't exist."""
        from uuid import uuid4

        from backend.infrastructure.auth.security import PasswordHasher
        from backend.infrastructure.repositories.user import UserRepository

        password_hasher = PasswordHasher()
        user_repo = UserRepository(db_session)
        unique_suffix = uuid4().hex[:6]
        user = await user_repo.create_user(
            username=f"nocreate_{unique_suffix}",
            password_hash=password_hasher.hash_password("TestPass123"),
        )
        # Don't create preferences - let update handle it

        app = UserPreferencesApplication(db_session)
        request = PreferencesUpdateRequest(theme="dark")

        await app.update_user_preferences(user, request)

        # Verify preferences were created with update applied
        prefs = await app.get_user_preferences(user)
        assert prefs.theme == "dark"
        assert prefs.font_size == "m"  # Default value

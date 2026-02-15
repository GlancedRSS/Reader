"""Unit tests for UserPreferenceConfig - user preference definitions and validation."""

import pytest

from backend.domain.user.preferences import (
    PreferenceField,
    UserPreferenceConfig,
)


class TestPreferenceField:
    """Test PreferenceField class."""

    def test_preference_field_init(self):
        """Should initialize with all parameters."""
        field = PreferenceField(
            field_type=str,
            choices=("a", "b", "c"),
            default="a",
            description="Test field",
        )

        assert field.field_type is str
        assert field.choices == ("a", "b", "c")
        assert field.default == "a"
        assert field.description == "Test field"

    def test_preference_field_validate_success(self):
        """Should validate when value is in choices."""
        field = PreferenceField(
            field_type=str,
            choices=("valid", "choice"),
            default="valid",
        )

        result = field.validate("valid")

        assert result == "valid"

    def test_preference_field_validate_wrong_type(self):
        """Should convert and validate when value is wrong type."""
        field = PreferenceField(
            field_type=int,  # Expects int
            choices=(1, 2, 3),
            default=1,
        )

        result = field.validate(2)  # Int value

        assert result == 2

    def test_preference_field_validate_not_in_choices(self):
        """Should raise ValueError when value not in choices."""
        field = PreferenceField(
            field_type=str,
            choices=("a", "b"),
            default="a",
        )

        with pytest.raises(ValueError, match="must be one of"):
            field.validate("c")


class TestUserPreferenceConfig:
    """Test UserPreferenceConfig class."""

    def test_get_defaults_returns_all_defaults(self):
        """Should return dictionary of all default values."""
        defaults = UserPreferenceConfig.get_defaults()

        # Check a few known defaults
        assert defaults["theme"] == "system"
        assert defaults["show_article_thumbnails"] is True
        assert defaults["app_layout"] == "split"
        assert defaults["article_layout"] == "grid"

    def test_get_field_names_returns_all_fields(self):
        """Should return set of all valid field names."""
        fields = UserPreferenceConfig.get_field_names()

        expected_fields = {
            "theme",
            "show_article_thumbnails",
            "app_layout",
            "article_layout",
            "font_spacing",
            "font_size",
            "feed_sort_order",
            "show_feed_favicons",
            "date_format",
            "time_format",
            "language",
            "auto_mark_as_read",
            "estimated_reading_time",
            "show_summaries",
        }

        assert fields == expected_fields

    def test_get_field_returns_valid_field(self):
        """Should return specific field definition."""
        field = UserPreferenceConfig.get_field("theme")

        assert isinstance(field, PreferenceField)
        assert field.field_type is str
        assert field.choices == ("light", "dark", "system")
        assert field.default == "system"

    def test_get_field_unknown_raises(self):
        """Should raise ValueError for unknown field name."""
        with pytest.raises(ValueError, match="Unknown preference field"):
            UserPreferenceConfig.get_field("unknown_field")

    def test_validate_preference_valid_string(self):
        """Should validate string preference."""
        config = UserPreferenceConfig()

        result = config.validate_preference("theme", "dark")

        assert result == "dark"

    def test_validate_preference_valid_bool(self):
        """Should validate boolean preference."""
        config = UserPreferenceConfig()

        result = config.validate_preference("show_article_thumbnails", False)

        assert result is False

    def test_validate_preference_valid_string_choice(self):
        """Should validate string preference choice."""
        config = UserPreferenceConfig()

        result = config.validate_preference("font_size", "l")

        assert result == "l"

    def test_validate_preference_invalid_choice(self):
        """Should raise ValueError for invalid choice."""
        config = UserPreferenceConfig()

        with pytest.raises(ValueError, match="must be one of"):
            config.validate_preference("theme", "invalid_choice")

    def test_validate_preference_invalid_value(self):
        """Should raise ValueError for invalid value not in choices."""
        config = UserPreferenceConfig()

        with pytest.raises(ValueError, match="must be one of"):
            config.validate_preference("font_size", "invalid_size")


class TestValidatePreferences:
    """Test validate_preferences method."""

    def test_validate_preferences_all_valid(self):
        """Should pass when all preferences are valid."""
        config = UserPreferenceConfig()
        preferences = {
            "theme": "dark",
            "show_article_thumbnails": False,
            "app_layout": "focus",
        }

        result = config.validate_preferences(preferences)

        assert result == preferences

    def test_validate_preferences_unknown_field_raises(self):
        """Should raise ValueError for unknown field."""
        config = UserPreferenceConfig()

        with pytest.raises(ValueError, match="Unknown preference field"):
            config.validate_preferences({"unknown_field": "value"})

    def test_validate_preferences_invalid_values_raises(self):
        """Should raise ValueError for invalid values."""
        config = UserPreferenceConfig()

        with pytest.raises(ValueError, match="must be one of"):
            config.validate_preferences({"theme": "invalid_choice"})


class TestMergeWithDefaults:
    """Test merge_with_defaults method."""

    def test_merge_with_defaults_no_updates(self):
        """Should return all defaults when no updates provided."""
        config = UserPreferenceConfig()
        defaults = config.get_defaults()

        result = config.merge_with_defaults({})

        assert result == defaults

    def test_merge_with_defaults_overrides_defaults(self):
        """Should override defaults with provided values."""
        config = UserPreferenceConfig()

        result = config.merge_with_defaults({"theme": "dark"})

        assert result["theme"] == "dark"
        # Other defaults should still be present
        assert "show_article_thumbnails" in result

    def test_merge_with_defaults_preserves_valid_updates(self):
        """Should preserve valid updates while merging defaults."""
        config = UserPreferenceConfig()
        updates = {"theme": "dark", "app_layout": "focus"}

        result = config.merge_with_defaults(updates)

        assert result["theme"] == "dark"
        assert result["app_layout"] == "focus"

    def test_merge_with_defaults_filters_invalid_updates(self):
        """Should raise ValueError for invalid updates."""
        config = UserPreferenceConfig()

        with pytest.raises(ValueError, match="Unknown preference field"):
            config.merge_with_defaults({"unknown_field": "value"})

"""Unit tests for UserPreferenceConfig domain logic."""

import pytest

from backend.domain.user import PreferenceField, UserPreferenceConfig


class TestPreferenceField:
    """Test PreferenceField class."""

    def test_init_with_choices(self):
        """Should create field with choices constraint."""
        field = PreferenceField(
            field_type=str,
            choices=("light", "dark", "system"),
            default="system",
        )
        assert field.field_type is str
        assert field.choices == ("light", "dark", "system")
        assert field.default == "system"

    def test_init_without_choices(self):
        """Should create field without choices constraint."""
        field = PreferenceField(field_type=bool, default=True)
        assert field.field_type is bool
        assert field.choices is None
        assert field.default is True

    def test_validate_with_valid_choice(self):
        """Should accept value in allowed choices."""
        field = PreferenceField(
            field_type=str,
            choices=("light", "dark", "system"),
            default="system",
        )
        result = field.validate("light")
        assert result == "light"

    def test_validate_with_invalid_choice(self):
        """Should reject value not in allowed choices."""
        field = PreferenceField(
            field_type=str,
            choices=("light", "dark", "system"),
            default="system",
        )
        with pytest.raises(ValueError, match="must be one of"):
            field.validate("invalid")

    def test_validate_without_choices(self):
        """Should accept any value when no choices constraint."""
        field = PreferenceField(field_type=bool, default=True)
        assert field.validate(True) is True
        assert field.validate(False) is False


class TestUserPreferenceConfig:
    """Test UserPreferenceConfig class."""

    def test_fields_contains_all_expected_preferences(self):
        """Should have all expected preference fields defined."""
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
        assert set(UserPreferenceConfig.FIELDS.keys()) == expected_fields

    def test_get_defaults_returns_all_fields(self):
        """Should return defaults for all preference fields."""
        defaults = UserPreferenceConfig.get_defaults()
        assert set(defaults.keys()) == set(UserPreferenceConfig.FIELDS.keys())

    def test_get_defaults_returns_correct_values(self):
        """Should return correct default values."""
        defaults = UserPreferenceConfig.get_defaults()
        assert defaults["theme"] == "system"
        assert defaults["show_article_thumbnails"] is True
        assert defaults["app_layout"] == "split"
        assert defaults["article_layout"] == "grid"
        assert defaults["font_spacing"] == "normal"
        assert defaults["font_size"] == "m"
        assert defaults["feed_sort_order"] == "recent_first"
        assert defaults["show_feed_favicons"] is True
        assert defaults["date_format"] == "relative"
        assert defaults["time_format"] == "12h"
        assert defaults["language"] == "en"
        assert defaults["auto_mark_as_read"] == "disabled"
        assert defaults["estimated_reading_time"] is True
        assert defaults["show_summaries"] is True

    def test_get_field_names_returns_all_field_names(self):
        """Should return set of all field names."""
        field_names = UserPreferenceConfig.get_field_names()
        assert isinstance(field_names, set)
        assert len(field_names) == 14

    def test_get_field_returns_valid_field(self):
        """Should return PreferenceField for valid field name."""
        field = UserPreferenceConfig.get_field("theme")
        assert isinstance(field, PreferenceField)
        assert field.field_type is str
        assert field.choices == ("light", "dark", "system")

    def test_get_field_raises_for_invalid_field(self):
        """Should raise ValueError for unknown field name."""
        with pytest.raises(ValueError, match="Unknown preference field"):
            UserPreferenceConfig.get_field("invalid_field")

    def test_validate_preference_with_valid_value(self):
        """Should validate and return valid preference value."""
        result = UserPreferenceConfig.validate_preference("theme", "dark")
        assert result == "dark"

    def test_validate_preference_with_invalid_choice(self):
        """Should raise ValueError for invalid choice value."""
        with pytest.raises(ValueError, match="must be one of"):
            UserPreferenceConfig.validate_preference("theme", "invalid")

    def test_validate_preference_with_type_coercion(self):
        """Should coerce string to correct type."""
        result = UserPreferenceConfig.validate_preference(
            "show_article_thumbnails", "true"
        )
        # String "true" should be coerced to bool True
        assert isinstance(result, bool)

    def test_validate_preference_raises_for_unknown_field(self):
        """Should raise ValueError for unknown field name."""
        with pytest.raises(ValueError, match="Unknown preference field"):
            UserPreferenceConfig.validate_preference("unknown_field", "value")

    def test_validate_preferences_with_valid_data(self):
        """Should validate dictionary of preferences."""
        preferences = {
            "theme": "dark",
            "show_article_thumbnails": False,
            "font_size": "xl",
        }
        result = UserPreferenceConfig.validate_preferences(preferences)
        assert result["theme"] == "dark"
        assert result["show_article_thumbnails"] is False
        assert result["font_size"] == "xl"

    def test_validate_preferences_with_invalid_field(self):
        """Should raise ValueError for unknown field in dictionary."""
        with pytest.raises(ValueError, match="Unknown preference field"):
            UserPreferenceConfig.validate_preferences(
                {"invalid_field": "value"}
            )

    def test_validate_preferences_with_invalid_value(self):
        """Should raise ValueError for invalid value."""
        with pytest.raises(ValueError, match="must be one of"):
            UserPreferenceConfig.validate_preferences({"theme": "invalid"})

    def test_merge_with_defaults(self):
        """Should merge updates with default values."""
        updates = {"theme": "dark", "show_article_thumbnails": False}
        result = UserPreferenceConfig.merge_with_defaults(updates)
        assert result["theme"] == "dark"
        assert result["show_article_thumbnails"] is False
        assert result["font_size"] == "m"  # Default value

    def test_merge_with_defaults_validates_updates(self):
        """Should validate updates when merging with defaults."""
        with pytest.raises(ValueError, match="must be one of"):
            UserPreferenceConfig.merge_with_defaults({"theme": "invalid"})

    def test_all_choice_fields_have_valid_defaults(self):
        """Ensure all choice fields have defaults that are valid choices."""
        defaults = UserPreferenceConfig.get_defaults()
        for field_name, field in UserPreferenceConfig.FIELDS.items():
            if field.choices:
                assert defaults[field_name] in field.choices, (
                    f"Field '{field_name}' default '{defaults[field_name]}' "
                    f"is not in choices {field.choices}"
                )

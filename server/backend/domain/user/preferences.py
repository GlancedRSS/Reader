"""User preference field definitions and validation rules."""

from typing import Any


class PreferenceField:
    """Definition for a single user preference field."""

    def __init__(
        self,
        field_type: type,
        choices: tuple[str, ...] | None = None,
        default: Any = None,
        description: str = "",
    ):
        """Initialize a preference field definition.

        Args:
            field_type: The expected type for the preference value.
            choices: Optional tuple of allowed values for enum-like preferences.
            default: The default value for this preference.
            description: Human-readable description of the preference.

        """
        self.field_type = field_type
        self.choices = choices
        self.default = default
        self.description = description

    def validate(self, value: Any) -> Any:
        """Validate a value against this field definition.

        Args:
            value: The value to validate.

        Returns:
            The validated value.

        Raises:
            ValueError: If the value is not in the allowed choices.

        """
        if self.choices and value not in self.choices:
            raise ValueError(
                f"Value must be one of {self.choices}, got '{value}'"
            )
        return value


class UserPreferenceConfig:
    """Central configuration for all user preferences and their validation."""

    FIELDS = {
        "theme": PreferenceField(
            field_type=str,
            choices=("light", "dark", "system"),
            default="system",
            description="Theme preference for the application",
        ),
        "show_article_thumbnails": PreferenceField(
            field_type=bool,
            default=True,
            description="Show article thumbnails in article lists",
        ),
        "app_layout": PreferenceField(
            field_type=str,
            choices=("split", "focus"),
            default="split",
            description="Overall application layout style",
        ),
        "article_layout": PreferenceField(
            field_type=str,
            choices=("grid", "list", "magazine"),
            default="grid",
            description="Article display layout",
        ),
        "font_spacing": PreferenceField(
            field_type=str,
            choices=("compact", "normal", "comfortable"),
            default="normal",
            description="Text spacing/line height preference",
        ),
        "font_size": PreferenceField(
            field_type=str,
            choices=("xs", "s", "m", "l", "xl"),
            default="m",
            description="Font size preference",
        ),
        "feed_sort_order": PreferenceField(
            field_type=str,
            choices=("alphabetical", "recent_first"),
            default="recent_first",
            description="Default sorting order for feeds",
        ),
        "show_feed_favicons": PreferenceField(
            field_type=bool,
            default=True,
            description="Show feed favicons in the UI",
        ),
        "date_format": PreferenceField(
            field_type=str,
            choices=("relative", "absolute"),
            default="relative",
            description="Date display format",
        ),
        "time_format": PreferenceField(
            field_type=str,
            choices=("12h", "24h"),
            default="12h",
            description="Time display format",
        ),
        "language": PreferenceField(
            field_type=str,
            default="en",
            description="Interface language (ISO 639-1 two-letter code)",
        ),
        "auto_mark_as_read": PreferenceField(
            field_type=str,
            choices=("disabled", "7_days", "14_days", "30_days"),
            default="disabled",
            description="Auto-mark articles as read after specified days",
        ),
        "estimated_reading_time": PreferenceField(
            field_type=bool,
            default=True,
            description="Show estimated reading time for articles",
        ),
        "show_summaries": PreferenceField(
            field_type=bool,
            default=True,
            description="Show article summaries",
        ),
    }

    @classmethod
    def get_defaults(cls) -> dict[str, Any]:
        """Get all default preference values.

        Returns:
            Dictionary mapping field names to their default values.

        """
        return {
            field_name: field.default
            for field_name, field in cls.FIELDS.items()
        }

    @classmethod
    def get_field_names(cls) -> set[str]:
        """Get all valid field names.

        Returns:
            Set of all valid preference field names.

        """
        return set(cls.FIELDS.keys())

    @classmethod
    def get_field(cls, field_name: str) -> PreferenceField:
        """Get a specific field definition.

        Args:
            field_name: The name of the preference field.

        Returns:
            The PreferenceField definition for the given field name.

        Raises:
            ValueError: If the field name is not recognized.

        """
        if field_name not in cls.FIELDS:
            raise ValueError(f"Unknown preference field: '{field_name}'")
        return cls.FIELDS[field_name]

    @classmethod
    def validate_preference(cls, field_name: str, value: Any) -> Any:
        """Validate a single preference value.

        Args:
            field_name: The name of the preference field.
            value: The value to validate.

        Returns:
            The validated and type-converted value.

        Raises:
            ValueError: If the field name is unknown or value is invalid.

        """
        field = cls.get_field(field_name)

        if not isinstance(value, field.field_type):
            try:
                value = field.field_type(value)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Field '{field_name}' must be of type {field.field_type.__name__}, "
                    f"got {type(value).__name__}"
                ) from None

        return field.validate(value)

    @classmethod
    def validate_preferences(
        cls, preferences: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate a dictionary of preferences.

        Args:
            preferences: Dictionary of preference field names to values.

        Returns:
            Dictionary of validated preference values.

        Raises:
            ValueError: If any field name is unknown or value is invalid.

        """
        validated = {}

        for field_name, value in preferences.items():
            if field_name not in cls.FIELDS:
                raise ValueError(f"Unknown preference field: '{field_name}'")

            validated[field_name] = cls.validate_preference(field_name, value)

        return validated

    @classmethod
    def merge_with_defaults(cls, updates: dict[str, Any]) -> dict[str, Any]:
        """Merge updates with default values.

        Args:
            updates: Dictionary of preference updates to apply.

        Returns:
            Dictionary with all preference values, merging defaults with updates.

        """
        merged = cls.get_defaults()
        validated_updates = cls.validate_preferences(updates)
        merged.update(validated_updates)

        return merged

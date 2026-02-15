"""Tag name and ownership validation."""

import re


class TagValidationDomain:
    """Tag name and ownership validation."""

    MAX_TAG_NAME_LENGTH = 64
    """Maximum length for tag names."""

    @classmethod
    def validate_tag_name(cls, name: str) -> str:
        """Validate and sanitize tag name according to business rules.

        Database constraints handle: NOT NULL, max length, uniqueness per user.
        This validation ensures non-empty names and returns sanitized name.

        Args:
            name: The tag name to validate

        Returns:
            Sanitized tag name

        Raises:
            ValueError: If tag name is empty or too long

        """
        if not name:
            raise ValueError("Tag name cannot be empty")

        sanitized = cls._sanitize_tag_name(name)

        if not sanitized:
            raise ValueError("Tag name cannot be empty")

        if len(sanitized) > cls.MAX_TAG_NAME_LENGTH:
            raise ValueError(
                f"Tag name cannot exceed {cls.MAX_TAG_NAME_LENGTH} characters"
            )

        return sanitized

    @classmethod
    def validate_tag_update(cls, name: str | None) -> str | None:
        """Validate tag update request.

        Args:
            name: The new tag name (None if not changing)

        Returns:
            Sanitized tag name, or None if name was None

        Raises:
            ValueError: If validation fails

        """
        if name is not None:
            return cls.validate_tag_name(name)

        return None

    @classmethod
    def _sanitize_tag_name(cls, name: str) -> str:
        """Sanitize tag name by removing control characters and trimming whitespace.

        Removes all control characters (including newlines, tabs, etc.),
        strips leading/trailing whitespace, and collapses internal whitespace
        to single spaces.

        Args:
            name: Raw tag name input

        Returns:
            Sanitized tag name

        """
        sanitized = re.sub(r"[\x00-\x1F\x7F-\x9F]", " ", name)
        sanitized = re.sub(r"\s+", " ", sanitized)
        return sanitized.strip()

"""Tag name and ownership validation."""

import re


class TagValidationDomain:
    """Tag name and ownership validation."""

    MAX_TAG_NAME_LENGTH = 64

    @classmethod
    def validate_tag_name(cls, name: str) -> str:
        """Validate and sanitize tag name (DB handles NOT NULL, max length, uniqueness)."""
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
        """Validate tag update request."""
        if name is not None:
            return cls.validate_tag_name(name)

        return None

    @classmethod
    def _sanitize_tag_name(cls, name: str) -> str:
        """Sanitize tag name: remove control chars, trim whitespace, collapse internal spaces."""
        sanitized = re.sub(r"[\x00-\x1F\x7F-\x9F]", " ", name)
        sanitized = re.sub(r"\s+", " ", sanitized)
        return sanitized.strip()

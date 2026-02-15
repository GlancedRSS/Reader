"""Unit tests for TagValidationDomain - tag name and ownership validation."""

import pytest

from backend.domain.tag.validation import TagValidationDomain


class TestValidateTagName:
    """Test tag name validation."""

    def test_validate_tag_name_valid(self):
        """Should accept valid tag name."""
        result = TagValidationDomain.validate_tag_name("Technology")

        assert result == "Technology"

    def test_validate_tag_name_trims_whitespace(self):
        """Should trim and normalize whitespace."""
        result = TagValidationDomain.validate_tag_name("  Tech  News  ")

        assert result == "Tech News"

    def test_validate_tag_name_removes_control_chars(self):
        """Should remove control characters."""
        result = TagValidationDomain.validate_tag_name("Tech\tNews\rForum")

        # Should remove newlines, tabs, carriage returns
        assert "\t" not in result
        assert "\r" not in result
        assert "\n" not in result

    def test_validate_tag_name_collapses_whitespace(self):
        """Should collapse multiple whitespace to single space."""
        result = TagValidationDomain.validate_tag_name("Tech    News")

        assert result == "Tech News"

    def test_validate_tag_name_too_long_raises(self):
        """Should raise ValueError for name above max length."""
        # MAX_TAG_NAME_LENGTH is a class attribute
        max_length = TagValidationDomain.MAX_TAG_NAME_LENGTH

        with pytest.raises(ValueError, match="cannot exceed"):
            TagValidationDomain.validate_tag_name("a" * (max_length + 1))

    def test_validate_tag_name_empty_raises(self):
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TagValidationDomain.validate_tag_name("")

    def test_validate_tag_name_only_control_chars_raises(self):
        """Should raise ValueError for name with only control characters."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TagValidationDomain.validate_tag_name("\x00\x1f\x7f\x9f")


class TestValidateTagUpdate:
    """Test tag update validation."""

    def test_validate_tag_update_with_name(self):
        """Should return sanitized name when name provided."""
        result = TagValidationDomain.validate_tag_update("New Name")

        assert result == "New Name"

    def test_validate_tag_update_no_name_returns_none(self):
        """Should return None when no name provided."""
        result = TagValidationDomain.validate_tag_update(name=None)

        assert result is None

    def test_validate_tag_update_invalid_name_raises(self):
        """Should raise ValueError when validation fails."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TagValidationDomain.validate_tag_update("")


class TestSanitizeTagName:
    """Test tag name sanitization."""

    def test_sanitize_tag_name_normal_text(self):
        """Should pass through normal text."""
        result = TagValidationDomain._sanitize_tag_name("Python Programming")

        assert result == "Python Programming"

    def test_sanitize_tag_name_removes_newlines(self):
        """Should remove newline characters."""
        result = TagValidationDomain._sanitize_tag_name("Tech\r\nForum")

        assert "\r" not in result
        assert "\n" not in result

    def test_sanitize_tag_name_removes_tabs(self):
        """Should remove tab characters."""
        result = TagValidationDomain._sanitize_tag_name("Tech\t\tForum")

        assert "\t" not in result

    def test_sanitize_tag_name_removes_form_feed(self):
        """Should remove form feed characters."""
        result = TagValidationDomain._sanitize_tag_name("Tech\x00Forum")

        assert "\x00" not in result
        assert "\x1f" not in result

    def test_sanitize_tag_name_trims_whitespace(self):
        """Should trim leading/trailing whitespace."""
        result = TagValidationDomain._sanitize_tag_name("  Tech Forum  ")

        assert result == "Tech Forum"

    def test_sanitize_tag_name_collapses_spaces(self):
        """Should collapse multiple spaces to one."""
        result = TagValidationDomain._sanitize_tag_name("Tech    Forum")

        assert result == "Tech Forum"

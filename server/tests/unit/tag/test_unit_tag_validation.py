"""Unit tests for tag domain validation."""

import pytest

from backend.domain.tag import TagValidationDomain


class TestTagNameValidation:
    """Test tag name validation."""

    def test_validate_tag_name_with_valid_names(self):
        """Should accept valid tag names."""
        valid_names = [
            "Work",
            "Tech News",
            "Blogs",
            "a",
            "1",
            "News 2024",
            "python",
            "JavaScript",
        ]

        for name in valid_names:
            TagValidationDomain.validate_tag_name(name)

    def test_validate_tag_name_with_empty_string_raises(self):
        """Should raise ValueError for empty string."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TagValidationDomain.validate_tag_name("")

    def test_validate_tag_name_with_whitespace_only_raises(self):
        """Should raise ValueError for whitespace-only name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TagValidationDomain.validate_tag_name("   ")

    def test_validate_tag_name_with_too_long_name_raises(self):
        """Should raise ValueError for name exceeding max length."""
        long_name = "a" * 65
        with pytest.raises(ValueError, match="exceed 64"):
            TagValidationDomain.validate_tag_name(long_name)

    def test_validate_tag_name_at_exactly_max_length(self):
        """Should accept name at exactly max length."""
        name = "a" * 64
        TagValidationDomain.validate_tag_name(name)

    def test_validate_tag_name_trims_leading_whitespace(self):
        """Should trim leading whitespace from name."""
        name = "  My Tag"
        result = TagValidationDomain.validate_tag_name(name)
        assert result == "My Tag"

    def test_validate_tag_name_trims_trailing_whitespace(self):
        """Should trim trailing whitespace from name."""
        name = "My Tag  "
        result = TagValidationDomain.validate_tag_name(name)
        assert result == "My Tag"

    def test_validate_tag_name_trims_both_sides(self):
        """Should trim both leading and trailing whitespace."""
        name = "  My Tag  "
        result = TagValidationDomain.validate_tag_name(name)
        assert result == "My Tag"

    def test_validate_tag_name_collapses_internal_whitespace(self):
        """Should collapse multiple internal spaces to single space."""
        name = "My    Tag    Name"
        result = TagValidationDomain.validate_tag_name(name)
        assert result == "My Tag Name"

    def test_validate_tag_name_removes_control_characters(self):
        """Should remove control characters from name."""
        name = "My\tTag\nName"
        result = TagValidationDomain.validate_tag_name(name)
        assert result == "My Tag Name"
        assert "\t" not in result
        assert "\n" not in result

    def test_validate_tag_name_with_newline_raises_after_sanitization(
        self,
    ):
        """Should raise ValueError if name is only newlines."""
        name = "\n\n\n"
        with pytest.raises(ValueError, match="cannot be empty"):
            TagValidationDomain.validate_tag_name(name)


class TestTagUpdateValidation:
    """Test tag update validation."""

    def test_validate_tag_update_with_valid_name(self):
        """Should accept valid name for update."""
        result = TagValidationDomain.validate_tag_update("Updated Name")
        assert result == "Updated Name"

    def test_validate_tag_update_with_none_returns_none(self):
        """Should return None when name is None (no update)."""
        result = TagValidationDomain.validate_tag_update(None)
        assert result is None

    def test_validate_tag_update_with_invalid_name_raises(self):
        """Should raise ValueError for invalid name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TagValidationDomain.validate_tag_update("")

    def test_validate_tag_update_with_too_long_name_raises(self):
        """Should raise ValueError for name exceeding max length."""
        long_name = "a" * 65
        with pytest.raises(ValueError, match="exceed 64"):
            TagValidationDomain.validate_tag_update(long_name)


class TestTagSanitization:
    """Test tag name sanitization."""

    def test_sanitize_removes_null_byte(self):
        """Should remove null bytes from name."""
        name = "My\x00Tag"
        result = TagValidationDomain._sanitize_tag_name(name)
        assert "\x00" not in result

    def test_sanitize_removes_all_control_chars(self):
        """Should remove all control characters (0x00-0x1F, 0x7F-0x9F)."""
        # Contains various control chars
        name = "My\x01\x02\x1f\x7f\x80\x9fTag"
        result = TagValidationDomain._sanitize_tag_name(name)
        # All control chars should be replaced with spaces and collapsed
        assert "My Tag" == result

    def test_sanitize_preserves_unicode(self):
        """Should preserve Unicode characters in name."""
        name = "日本語 Tag العربية"
        result = TagValidationDomain._sanitize_tag_name(name)
        assert result == name

    def test_sanitize_preserves_special_chars(self):
        """Should preserve special characters like hyphens and underscores."""
        name = "my-tag_name"
        result = TagValidationDomain._sanitize_tag_name(name)
        assert result == name

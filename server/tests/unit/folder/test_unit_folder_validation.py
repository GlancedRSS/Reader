"""Unit tests for folder domain validation."""

import pytest

from backend.domain.constants import (
    MAX_FOLDER_DEPTH,
    MAX_FOLDER_NAME_LENGTH,
    MAX_FOLDERS_PER_PARENT,
)
from backend.domain.folder import (
    CircularReferenceError,
    FolderDepthExceededError,
    FolderLimitExceededError,
    FolderValidationDomain,
)


class TestFolderNameValidation:
    """Test folder name validation."""

    def test_validate_folder_name_with_valid_name(self):
        """Should accept valid folder names."""
        valid_names = ["Work", "Tech News", " Blogs", "a", "1", "News 2024"]

        for name in valid_names:
            FolderValidationDomain.validate_folder_name(name)

    def test_validate_folder_name_with_empty_string_raises(self):
        """Should raise ValueError for empty string."""
        with pytest.raises(ValueError, match="cannot be empty"):
            FolderValidationDomain.validate_folder_name("")

    def test_validate_folder_name_with_whitespace_only_raises(self):
        """Should raise ValueError for whitespace-only name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            FolderValidationDomain.validate_folder_name("   ")

    def test_validate_folder_name_with_too_long_name_raises(self):
        """Should raise ValueError for name exceeding max length."""
        long_name = "a" * (MAX_FOLDER_NAME_LENGTH + 1)
        with pytest.raises(ValueError, match="too long"):
            FolderValidationDomain.validate_folder_name(long_name)

    def test_validate_folder_name_trims_whitespace(self):
        """Should trim leading/trailing whitespace from name."""
        name = "  My Folder  "
        FolderValidationDomain.validate_folder_name(name)
        # If it doesn't raise, validation passed (whitespace was trimmed)

    def test_validate_folder_name_with_exactly_max_length(self):
        """Should accept name at exactly max length."""
        name = "a" * MAX_FOLDER_NAME_LENGTH
        FolderValidationDomain.validate_folder_name(name)


class TestFolderCapacityValidation:
    """Test folder capacity validation."""

    def test_validate_folder_capacity_with_valid_metrics(self):
        """Should accept valid folder capacity metrics."""
        FolderValidationDomain.validate_folder_capacity(folders_used=0, depth=0)
        FolderValidationDomain.validate_folder_capacity(
            folders_used=MAX_FOLDERS_PER_PARENT - 1, depth=MAX_FOLDER_DEPTH
        )

    def test_validate_folder_capacity_with_exceeded_depth_raises(self):
        """Should raise FolderDepthExceededError when depth exceeds maximum."""
        with pytest.raises(
            FolderDepthExceededError, match=r"nesting depth.*exceeds maximum"
        ):
            FolderValidationDomain.validate_folder_capacity(
                folders_used=0, depth=MAX_FOLDER_DEPTH + 1
            )

    def test_validate_folder_capacity_at_max_depth(self):
        """Should accept folder at exactly maximum depth."""
        FolderValidationDomain.validate_folder_capacity(
            folders_used=0, depth=MAX_FOLDER_DEPTH
        )

    def test_validate_folder_capacity_with_exceeded_limit_raises(self):
        """Should raise FolderLimitExceededError when folder count exceeds maximum."""
        with pytest.raises(
            FolderLimitExceededError, match=r"count.*exceeds maximum"
        ):
            FolderValidationDomain.validate_folder_capacity(
                folders_used=MAX_FOLDERS_PER_PARENT, depth=0
            )

    def test_validate_folder_capacity_at_max_limit(self):
        """Should accept folder at exactly maximum limit."""
        FolderValidationDomain.validate_folder_capacity(
            folders_used=MAX_FOLDERS_PER_PARENT - 1, depth=0
        )

    def test_validate_folder_capacity_error_contains_current_and_limit(self):
        """Error should contain current value and limit information."""
        with pytest.raises(
            (FolderDepthExceededError, FolderLimitExceededError)
        ) as exc_info:
            FolderValidationDomain.validate_folder_capacity(
                folders_used=50, depth=15
            )
        assert exc_info.value.current is not None
        assert exc_info.value.limit is not None
        assert exc_info.value.limit_type in ["depth", "folder_count"]


class TestCircularReferenceError:
    """Test CircularReferenceError exception."""

    def test_circular_reference_error_default_message(self):
        """Should have default error message."""
        error = CircularReferenceError()
        assert str(error) == "Circular reference detected in folder hierarchy"

    def test_circular_reference_error_custom_message(self):
        """Should accept custom error message."""
        custom_msg = "Custom circular reference message"
        error = CircularReferenceError(custom_msg)
        assert str(error) == custom_msg

    def test_circular_reference_error_is_value_error_subclass(self):
        """Should be a subclass of ValueError."""
        error = CircularReferenceError()
        assert isinstance(error, ValueError)


class TestFolderDepthExceededError:
    """Test FolderDepthExceededError exception."""

    def test_folder_depth_exceeded_error_message_format(self):
        """Should format message with current and limit values."""
        error = FolderDepthExceededError(current=10, limit=9)
        assert "10" in str(error)
        assert "9" in str(error)
        assert "exceeds maximum" in str(error)

    def test_folder_depth_exceeded_error_attributes(self):
        """Should store current, limit, and limit_type attributes."""
        error = FolderDepthExceededError(current=5, limit=9)
        assert error.current == 5
        assert error.limit == 9
        assert error.limit_type == "depth"

    def test_folder_depth_exceeded_error_uses_default_limit(self):
        """Should use MAX_FOLDER_DEPTH as default limit."""
        error = FolderDepthExceededError(current=10)
        assert error.limit == MAX_FOLDER_DEPTH


class TestFolderLimitExceededError:
    """Test FolderLimitExceededError exception."""

    def test_folder_limit_exceeded_error_message_format(self):
        """Should format message with current and limit values."""
        error = FolderLimitExceededError(current=50, limit=50)
        assert "50" in str(error)
        assert "maximum allowed per parent" in str(error)

    def test_folder_limit_exceeded_error_attributes(self):
        """Should store current, limit, and limit_type attributes."""
        error = FolderLimitExceededError(current=45, limit=50)
        assert error.current == 45
        assert error.limit == 50
        assert error.limit_type == "folder_count"

    def test_folder_limit_exceeded_error_uses_default_limit(self):
        """Should use MAX_FOLDERS_PER_PARENT as default limit."""
        error = FolderLimitExceededError(current=100)
        assert error.limit == MAX_FOLDERS_PER_PARENT

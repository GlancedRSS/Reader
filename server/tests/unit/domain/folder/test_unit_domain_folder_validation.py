"""Unit tests for FolderValidationDomain - folder capacity and hierarchy validation."""

import pytest

from backend.domain.constants import (
    MAX_FOLDER_DEPTH,
    MAX_FOLDER_NAME_LENGTH,
    MAX_FOLDERS_PER_PARENT,
)
from backend.domain.folder.validation import (
    FolderDepthExceededError,
    FolderLimitExceededError,
    FolderValidationDomain,
)

# The actual validate_folder_name function is in utils.validators
# which returns different error messages than the domain wrapper
ERROR_TOO_LONG = r"Folder name too long \(max 16 characters\)"
ERROR_EMPTY = "Folder name cannot be empty"


class TestValidateFolderCapacity:
    """Test folder capacity validation."""

    def test_validate_folder_capacity_within_limits(self):
        """Should pass when folder count and depth are within limits."""
        result = FolderValidationDomain.validate_folder_capacity(
            folders_used=10, depth=3
        )

        assert result is None

    def test_validate_folder_capacity_exceeds_depth(self):
        """Should raise FolderDepthExceededError when depth exceeds maximum."""
        with pytest.raises(
            FolderDepthExceededError, match="exceeds maximum allowed"
        ):
            FolderValidationDomain.validate_folder_capacity(
                folders_used=10, depth=MAX_FOLDER_DEPTH + 1
            )

    def test_validate_folder_capacity_exceeds_folder_count(self):
        """Should raise FolderLimitExceededError when folder count exceeds maximum."""
        with pytest.raises(
            FolderLimitExceededError, match="exceeds maximum allowed"
        ):
            FolderValidationDomain.validate_folder_capacity(
                folders_used=MAX_FOLDERS_PER_PARENT + 1, depth=5
            )

    def test_validate_folder_capacity_exceeds_both_limits(self):
        """Should raise FolderDepthExceededError when depth limit is hit first."""
        with pytest.raises(
            FolderDepthExceededError, match="exceeds maximum allowed"
        ):
            FolderValidationDomain.validate_folder_capacity(
                folders_used=MAX_FOLDERS_PER_PARENT + 1,
                depth=MAX_FOLDER_DEPTH + 1,
            )

    def test_validate_folder_capacity_at_max_depth(self):
        """Should pass when exactly at max depth."""
        result = FolderValidationDomain.validate_folder_capacity(
            folders_used=10, depth=MAX_FOLDER_DEPTH
        )

        assert result is None

    def test_validate_folder_capacity_below_max_count(self):
        """Should pass when below max folder count."""
        result = FolderValidationDomain.validate_folder_capacity(
            folders_used=MAX_FOLDERS_PER_PARENT - 1, depth=3
        )

        assert result is None


class TestValidateFolderName:
    """Test folder name validation."""

    def test_validate_folder_name_valid(self):
        """Should pass when folder name is valid."""
        result = FolderValidationDomain.validate_folder_name("Tech")

        assert result is None

    def test_validate_folder_name_too_long_raises(self):
        """Should raise ValueError when folder name exceeds max length."""
        with pytest.raises(ValueError, match=ERROR_TOO_LONG):
            FolderValidationDomain.validate_folder_name(
                "a" * (MAX_FOLDER_NAME_LENGTH + 1)
            )

    def test_validate_folder_name_empty_raises(self):
        """Should raise ValueError when folder name is empty."""
        with pytest.raises(ValueError, match=ERROR_EMPTY):
            FolderValidationDomain.validate_folder_name("")

    def test_validate_folder_name_with_spaces(self):
        """Should pass when folder name has spaces (trimmed)."""
        result = FolderValidationDomain.validate_folder_name("  Tech  ")

        assert result is None

    def test_validate_folder_name_special_chars(self):
        """Should validate folder name via utils validator."""
        # The domain delegates to utils.validators.validate_folder_name
        # This tests that delegation works correctly
        result = FolderValidationDomain.validate_folder_name("Valid Folder!")

        assert result is None

"""Folder capacity, depth, and name validation."""

from backend.domain import (
    MAX_FOLDER_DEPTH,
    MAX_FOLDER_NAME_LENGTH,
    MAX_FOLDERS_PER_PARENT,
)


class CircularReferenceError(ValueError):
    """Exception when a circular reference would be created in folder hierarchy."""

    def __init__(
        self, message: str = "Circular reference detected in folder hierarchy"
    ):
        """Initialize a CircularReferenceError.

        Args:
            message: Error message to display

        """
        super().__init__(message)


class FolderLimitError(ValueError):
    """Base exception for folder limit violations (count or depth)."""

    def __init__(self, message: str, current: int, limit: int, limit_type: str):
        """Initialize a FolderLimitError.

        Args:
            message: Error message to display
            current: Current value that exceeded the limit
            limit: The limit that was exceeded
            limit_type: Type of limit (e.g., "depth", "folder_count")

        """
        super().__init__(message)
        self.current = current
        self.limit = limit
        self.limit_type = limit_type


class FolderDepthExceededError(FolderLimitError):
    """Exception raised when folder nesting depth is exceeded."""

    def __init__(self, current: int, limit: int = MAX_FOLDER_DEPTH):
        """Initialize a FolderDepthExceededError.

        Args:
            current: Current depth level
            limit: Maximum allowed depth

        """
        message = f"Folder nesting depth ({current}) exceeds maximum allowed ({limit})"
        super().__init__(message, current, limit, "depth")


class FolderLimitExceededError(FolderLimitError):
    """Exception raised when folder limit per parent is exceeded."""

    def __init__(self, current: int, limit: int = MAX_FOLDERS_PER_PARENT):
        """Initialize a FolderLimitExceededError.

        Args:
            current: Current folder count
            limit: Maximum allowed folders

        """
        message = f"Folder count ({current}) exceeds maximum allowed per parent ({limit})"
        super().__init__(message, current, limit, "folder_count")


class FolderValidationDomain:
    """Folder capacity, depth, and name validation."""

    @classmethod
    def validate_folder_capacity(cls, folders_used: int, depth: int) -> None:
        """Validate folder capacity against business rules.

        This is a database-agnostic validation that accepts
        the current capacity metrics as parameters and validates
        them against domain business rules.

        Args:
            folders_used: Current number of folders in the parent
            depth: Depth level for the new folder

        Raises:
            FolderDepthExceededError: If depth exceeds maximum
            FolderLimitExceededError: If folder count exceeds maximum

        """
        if depth > MAX_FOLDER_DEPTH:
            raise FolderDepthExceededError(depth, MAX_FOLDER_DEPTH)

        if folders_used >= MAX_FOLDERS_PER_PARENT:
            raise FolderLimitExceededError(folders_used, MAX_FOLDERS_PER_PARENT)

    @classmethod
    def validate_folder_name(cls, name: str) -> None:
        """Validate folder name.

        Args:
            name: Folder name to validate

        Raises:
            ValueError: If name is invalid

        """
        from backend.utils.validators import validate_folder_name

        validate_folder_name(name, MAX_FOLDER_NAME_LENGTH)

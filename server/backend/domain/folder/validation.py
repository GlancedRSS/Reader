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
        super().__init__(message)


class FolderLimitError(ValueError):
    """Base exception for folder limit violations (count or depth)."""

    def __init__(self, message: str, current: int, limit: int, limit_type: str):
        super().__init__(message)
        self.current = current
        self.limit = limit
        self.limit_type = limit_type


class FolderDepthExceededError(FolderLimitError):
    """Exception raised when folder nesting depth is exceeded."""

    def __init__(self, current: int, limit: int = MAX_FOLDER_DEPTH):
        message = f"Folder nesting depth ({current}) exceeds maximum allowed ({limit})"
        super().__init__(message, current, limit, "depth")


class FolderLimitExceededError(FolderLimitError):
    """Exception raised when folder limit per parent is exceeded."""

    def __init__(self, current: int, limit: int = MAX_FOLDERS_PER_PARENT):
        message = f"Folder count ({current}) exceeds maximum allowed per parent ({limit})"
        super().__init__(message, current, limit, "folder_count")


class FolderValidationDomain:
    """Folder capacity, depth, and name validation."""

    @classmethod
    def validate_folder_capacity(cls, folders_used: int, depth: int) -> None:
        """Validate folder capacity and depth against business rules (database-agnostic)."""
        if depth > MAX_FOLDER_DEPTH:
            raise FolderDepthExceededError(depth, MAX_FOLDER_DEPTH)

        if folders_used >= MAX_FOLDERS_PER_PARENT:
            raise FolderLimitExceededError(folders_used, MAX_FOLDERS_PER_PARENT)

    @classmethod
    def validate_folder_name(cls, name: str) -> None:
        """Validate folder name."""
        from backend.utils.validators import validate_folder_name

        validate_folder_name(name, MAX_FOLDER_NAME_LENGTH)

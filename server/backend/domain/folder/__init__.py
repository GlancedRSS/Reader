"""Folder validation, capacity management, and business rules."""

from .validation import (
    CircularReferenceError,
    FolderDepthExceededError,
    FolderLimitError,
    FolderLimitExceededError,
    FolderValidationDomain,
)

__all__ = [
    "CircularReferenceError",
    "FolderDepthExceededError",
    "FolderLimitError",
    "FolderLimitExceededError",
    "FolderValidationDomain",
]

"""Core business logic without infrastructure dependencies."""

from backend.domain.auth import (
    AuthDomain,
    AuthenticationError,
    AuthValidationDomain,
    InvalidCredentialsError,
    InvalidPasswordError,
)
from backend.domain.constants import (
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    MAX_ACTIVE_SESSIONS,
    MAX_BATCH_SIZE,
    MAX_FOLDER_DEPTH,
    MAX_FOLDER_NAME_LENGTH,
    MAX_FOLDERS_PER_PARENT,
    MAX_LIMIT,
    MAX_OPML_ATTRIBUTE_LENGTH,
    MAX_OPML_FILE_SIZE,
    MAX_OPML_NESTING_DEPTH,
    MAX_OPML_OUTLINES,
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
    OPML_FILE_EXPIRY_HOURS,
)
from backend.domain.enums import (
    FeedStatus,
    OpmlImportStatus,
    SubscriptionStatus,
)
from backend.domain.user import PreferenceField, UserPreferenceConfig

__all__ = [
    "DEFAULT_LIMIT",
    "DEFAULT_OFFSET",
    "MAX_ACTIVE_SESSIONS",
    "MAX_BATCH_SIZE",
    "MAX_FOLDERS_PER_PARENT",
    "MAX_FOLDER_DEPTH",
    "MAX_FOLDER_NAME_LENGTH",
    "MAX_LIMIT",
    "MAX_OPML_ATTRIBUTE_LENGTH",
    "MAX_OPML_FILE_SIZE",
    "MAX_OPML_NESTING_DEPTH",
    "MAX_OPML_OUTLINES",
    "MAX_PASSWORD_LENGTH",
    "MAX_USERNAME_LENGTH",
    "MIN_PASSWORD_LENGTH",
    "MIN_USERNAME_LENGTH",
    "OPML_FILE_EXPIRY_HOURS",
    "AuthDomain",
    "AuthValidationDomain",
    "AuthenticationError",
    "FeedStatus",
    "InvalidCredentialsError",
    "InvalidPasswordError",
    "OpmlImportStatus",
    "PreferenceField",
    "SubscriptionStatus",
    "UserPreferenceConfig",
]

"""Constants for validation limits, business rules, and configuration."""

DEFAULT_LIMIT = 50
"""Default number of items to return per page."""

MAX_LIMIT = 100
"""Maximum number of items allowed per page."""

DEFAULT_OFFSET = 0
"""Default offset for pagination."""

MAX_TAG_NAME_LENGTH = 64
"""Maximum length for tag names."""

MAX_FOLDER_DEPTH = 9
"""Maximum folder nesting depth (supports levels 0-9, 10 total levels)."""

MAX_FOLDERS_PER_PARENT = 50
"""Maximum number of child folders per parent folder for performance."""

MAX_BATCH_SIZE = 100
"""Maximum number of items in batch operations."""

MAX_FOLDER_NAME_LENGTH = 16
"""Maximum length of a folder name."""

MAX_OPML_FILE_SIZE = 16 * 1024 * 1024
"""Maximum OPML file size in bytes (16MB)."""

MAX_OPML_ATTRIBUTE_LENGTH = 1000
"""Maximum length of attribute values in OPML files."""

MAX_OPML_NESTING_DEPTH = 9
"""Maximum nesting depth of outline elements in OPML files."""

MAX_OPML_OUTLINES = 10000
"""Maximum number of outline elements in OPML files."""

OPML_FILE_EXPIRY_HOURS = 24
"""Number of hours before exported OPML files expire."""

MIN_USERNAME_LENGTH = 3
"""Minimum number of characters in a username."""

MAX_USERNAME_LENGTH = 20
"""Maximum number of characters in a username."""

MIN_PASSWORD_LENGTH = 8
"""Minimum number of characters in a password."""

MAX_PASSWORD_LENGTH = 128
"""Maximum number of characters in a password."""

MAX_ACTIVE_SESSIONS = 5
"""Maximum number of concurrent active sessions per user."""

"""Local filesystem storage client for app-level operations.

This provides local file storage functionality for the app, primarily for OPML
file uploads.
"""

import hashlib
from pathlib import Path

from backend.core.app import settings


class LocalStorageClient:
    """Local filesystem storage client for app-level operations.

    Provides file upload, download, and deletion operations for OPML files.
    """

    def __init__(
        self,
        base_path: str | None = None,
    ) -> None:
        """Initialize the local storage client.

        Args:
            base_path: Base directory for file storage (defaults to settings).

        Raises:
            ValueError: If base_path is not configured.

        """
        self._base_path = Path(
            base_path or getattr(settings, "storage_path", "") or ""
        )

        if not self._base_path:
            raise ValueError("Storage path (STORAGE_PATH) is not configured")

        self._base_path.mkdir(parents=True, exist_ok=True)

    def generate_storage_key(
        self, path: str, filename: str | None = None
    ) -> str:
        """Generate a storage key (relative path).

        New structure: users/{user_id}/{category}/{filename}

        Args:
            path: Full path prefix (e.g., "users/{user_id}/imports")
            filename: Filename (optional, for direct path only)

        Returns:
            Storage key path (relative to base_path).

        """
        if filename:
            return f"{path}/{filename}"
        return path

    def upload_file(
        self,
        key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a file to local storage.

        Args:
            key: Storage key (relative path).
            content: File content.
            content_type: MIME type (unused for local files, kept for API compatibility).
            metadata: Optional metadata dictionary (unused for local files).

        Returns:
            The storage key.

        Raises:
            OSError: If upload fails.

        """
        file_path = self._base_path / key

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)

        return key

    def upload_file_from_string(
        self,
        key: str,
        content: str,
        content_type: str = "application/xml",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a string as a file to local storage.

        Args:
            key: Storage key (relative path).
            content: File content as string.
            content_type: MIME type.
            metadata: Optional metadata dictionary.

        Returns:
            The storage key.

        """
        return self.upload_file(
            key, content.encode("utf-8"), content_type, metadata
        )

    def download_file(self, key: str) -> bytes:
        """Download a file from local storage.

        Args:
            key: Storage key (relative path).

        Returns:
            File content as bytes.

        Raises:
            FileNotFoundError: If key doesn't exist.

        """
        file_path = self._base_path / key

        if not file_path.exists():
            raise FileNotFoundError(key)

        return file_path.read_bytes()

    def download_file_as_string(self, key: str) -> str:
        """Download a file from local storage as string.

        Args:
            key: Storage key (relative path).

        Returns:
            File content as string.

        Raises:
            FileNotFoundError: If key doesn't exist.

        """
        content = self.download_file(key)
        return content.decode("utf-8")

    def delete_file(self, key: str) -> bool:
        """Delete a file from local storage.

        Args:
            key: Storage key (relative path).

        Returns:
            True if deleted, False if not found.

        """
        file_path = self._base_path / key

        if file_path.exists():
            file_path.unlink()
            return True

        return False

    def file_exists(self, key: str) -> bool:
        """Check if a file exists in local storage.

        Args:
            key: Storage key (relative path).

        Returns:
            True if file exists, False otherwise.

        """
        return (self._base_path / key).exists()

    @staticmethod
    def calculate_content_hash(content: bytes) -> str:
        """Calculate SHA-256 hash of content.

        Args:
            content: File content.

        Returns:
            Hexadecimal hash.

        """
        return hashlib.sha256(content).hexdigest()

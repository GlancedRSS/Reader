"""Local filesystem storage for OPML file operations."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from structlog import get_logger

from backend.core.app import settings

logger = get_logger(__name__)


class BaseLocalStorageClient:
    """Base client for local filesystem storage operations."""

    def __init__(self) -> None:
        """Initialize the local storage client."""
        self._base_path = Path(settings.storage_path)

        if not self._base_path:
            raise ValueError("Storage path (STORAGE_PATH) is not configured")

        self._base_path.mkdir(parents=True, exist_ok=True)

    def generate_storage_key(
        self, path: str, filename: str | None = None
    ) -> str:
        """Generate a storage key (relative path)."""
        if filename:
            return f"{path}/{filename}"
        return path

    async def upload_file(
        self,
        key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a file to local storage."""
        file_path = self._base_path / key

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)

        logger.info(
            "File uploaded to local storage",
            key=key,
            size=len(content),
            content_type=content_type,
        )

        return key

    async def download_file(self, key: str) -> bytes:
        """Download a file from local storage."""
        file_path = self._base_path / key

        if not file_path.exists():
            logger.warning("File not found in local storage", key=key)
            raise FileNotFoundError(key)

        content = file_path.read_bytes()

        logger.info(
            "File downloaded from local storage",
            key=key,
            size=len(content),
        )

        return content

    async def delete_file(self, key: str) -> bool:
        """Delete a file from local storage."""
        file_path = self._base_path / key

        if file_path.exists():
            file_path.unlink()
            logger.info("File deleted from local storage", key=key)
            return True

        return False

    async def delete_prefix(self, prefix: str) -> int:
        """Delete all files with a given prefix from local storage."""
        deleted_count = 0
        prefix_path = self._base_path / prefix

        if prefix_path.exists() and prefix_path.is_dir():
            for file_path in prefix_path.rglob("*"):
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1

            for dir_path in sorted(prefix_path.rglob("*"), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()

            logger.info(
                "Prefix deleted from local storage",
                prefix=prefix,
                deleted_count=deleted_count,
            )

        return deleted_count

    async def file_exists(self, key: str) -> bool:
        """Check if a file exists in local storage."""
        return (self._base_path / key).exists()

    def generate_download_url(
        self,
        key: str,
        expiration_seconds: int = 86400,
    ) -> str:
        """Generate a download URL for a file."""
        parts = key.split("/")
        if len(parts) >= 4 and parts[2] == "exports":
            filename = parts[3]
            return f"opml/download/{filename}"

        return f"opml/download/{key}"

    @staticmethod
    def calculate_content_hash(content: bytes) -> str:
        """Calculate SHA-256 hash of content."""
        import hashlib

        return hashlib.sha256(content).hexdigest()


class LocalOpmlStorage(BaseLocalStorageClient):
    """Local filesystem storage for OPML file operations."""

    async def upload_file(
        self,
        key: str,
        content: bytes,
        content_type: str = "application/xml",
        metadata: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Upload an OPML file to local storage."""
        if metadata is None and "expires_in_hours" in kwargs:
            expires_in_hours = kwargs["expires_in_hours"]
            if expires_in_hours:
                expires_at = datetime.now(UTC) + timedelta(
                    hours=expires_in_hours
                )
                metadata = {"expires-at": expires_at.isoformat()}

        return await super().upload_file(key, content, content_type, metadata)

import hashlib
from pathlib import Path

from backend.core.app import settings


class LocalStorageClient:
    def __init__(
        self,
        base_path: str | None = None,
    ) -> None:
        self._base_path = Path(
            base_path or getattr(settings, "storage_path", "") or ""
        )

        if not self._base_path:
            raise ValueError("Storage path (STORAGE_PATH) is not configured")

        self._base_path.mkdir(parents=True, exist_ok=True)

    def generate_storage_key(
        self, path: str, filename: str | None = None
    ) -> str:
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
        return self.upload_file(
            key, content.encode("utf-8"), content_type, metadata
        )

    def download_file(self, key: str) -> bytes:
        file_path = self._base_path / key

        if not file_path.exists():
            raise FileNotFoundError(key)

        return file_path.read_bytes()

    def download_file_as_string(self, key: str) -> str:
        content = self.download_file(key)
        return content.decode("utf-8")

    def delete_file(self, key: str) -> bool:
        file_path = self._base_path / key

        if file_path.exists():
            file_path.unlink()
            return True

        return False

    def file_exists(self, key: str) -> bool:
        return (self._base_path / key).exists()

    @staticmethod
    def calculate_content_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

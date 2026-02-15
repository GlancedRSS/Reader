"""Storage infrastructure for local filesystem."""

from backend.infrastructure.storage.local import (
    BaseLocalStorageClient,
    LocalOpmlStorage,
)

__all__ = [
    "BaseLocalStorageClient",
    "LocalOpmlStorage",
]

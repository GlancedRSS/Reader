"""OPML data access layer for import operations."""

import os
import time
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import OpmlImport, UserFeed


class OpmlRepository:
    """Repository for OPML import operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the OPML repository.

        Args:
            db: Async database session.

        """
        self.db = db

    async def find_import_by_id(
        self, import_id: UUID, user_id: UUID
    ) -> OpmlImport | None:
        """Get import record by ID with user filtering.

        Args:
            import_id: The import ID.
            user_id: The user ID.

        Returns:
            The OpmlImport if found and belongs to user, None otherwise.

        """
        stmt = select(OpmlImport).where(
            and_(
                OpmlImport.id == import_id,
                OpmlImport.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_feed_count(
        self, user_id: UUID, folder_id: UUID | None = None
    ) -> int:
        """Get count of user's feeds, optionally filtered by folder.

        Args:
            user_id: The user ID.
            folder_id: Optional folder ID to filter by.

        Returns:
            Count of feed subscriptions.

        """
        count_stmt = (
            select(func.count())
            .select_from(UserFeed)
            .where(UserFeed.user_id == user_id)
        )

        if folder_id:
            count_stmt = count_stmt.where(UserFeed.folder_id == folder_id)

        result = await self.db.execute(count_stmt)
        return result.scalar() or 0

    async def create_import_record(
        self,
        user_id: UUID,
        filename: str,
        storage_key: str | None = None,
        status: str = "pending",
    ) -> OpmlImport:
        """Create OPML import record.

        Args:
            user_id: The user ID.
            filename: The uploaded filename.
            storage_key: Optional local storage key for the uploaded file.
            status: The initial status (default: "pending").

        Returns:
            The created OpmlImport record.

        """
        opml_import = OpmlImport(
            user_id=user_id,
            filename=filename,
            storage_key=storage_key,
            status=status,
        )

        self.db.add(opml_import)
        await self.db.commit()
        await self.db.refresh(opml_import)
        return opml_import

    async def get_import_by_id(self, import_id: UUID) -> OpmlImport | None:
        """Get import record by ID.

        Args:
            import_id: The import ID.

        Returns:
            The OpmlImport if found, None otherwise.

        """
        return await self.db.get(OpmlImport, import_id)

    async def update_import_storage_key(
        self, import_id: UUID, storage_key: str
    ) -> None:
        """Update import record with storage key.

        Args:
            import_id: The import ID to update.
            storage_key: The local storage key where the file is stored.

        """
        opml_import = await self.get_import_by_id(import_id)
        if opml_import:
            opml_import.storage_key = storage_key
            await self.db.commit()

    async def update_import_status(
        self,
        import_id: UUID,
        status: str,
        total_feeds: int = 0,
        imported_feeds: int = 0,
        failed_feeds: int = 0,
        duplicate_feeds: int = 0,
        failed_feeds_log: list[dict[str, Any]] | None = None,
    ) -> None:
        """Update import record with processing results.

        Args:
            import_id: The import ID to update.
            status: The new status.
            total_feeds: Total feed count.
            imported_feeds: Successfully imported feed count.
            failed_feeds: Failed feed count.
            duplicate_feeds: Duplicate feed count.
            failed_feeds_log: List of failed feed details.

        """
        opml_import = await self.get_import_by_id(import_id)
        if opml_import:
            opml_import.status = status
            opml_import.total_feeds = total_feeds
            opml_import.imported_feeds = imported_feeds
            opml_import.failed_feeds = failed_feeds
            opml_import.duplicate_feeds = duplicate_feeds
            if failed_feeds_log is not None:
                opml_import.failed_feeds_log = failed_feeds_log
            await self.db.commit()

    async def get_opml_by_id(
        self, job_id: UUID, user_id: UUID
    ) -> OpmlImport | None:
        """Get OPML import operation by ID.

        Args:
            job_id: The job ID.
            user_id: The user ID for ownership check.

        Returns:
            The OpmlImport if found, None otherwise.

        """
        import_result = await self.db.execute(
            select(OpmlImport).where(
                OpmlImport.id == job_id,
                OpmlImport.user_id == user_id,
            )
        )
        import_record = import_result.scalar_one_or_none()
        if import_record:
            return import_record

        return None

    def ensure_file_directory(self, file_path: str) -> None:
        """Ensure the directory for a file path exists.

        Args:
            file_path: The file path for which to ensure directory exists.

        """
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)

    def save_opml_file(self, file_path: str, content: str) -> None:
        """Save OPML content to file.

        Args:
            file_path: The destination file path.
            content: The OPML content to write.

        """
        self.ensure_file_directory(file_path)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read_opml_file(self, file_path: str) -> str:
        """Read OPML content from file.

        Args:
            file_path: The file path to read.

        Returns:
            The file content as string.

        """
        with open(file_path, encoding="utf-8") as f:
            return f.read()

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists.

        Args:
            file_path: The file path to check.

        Returns:
            True if file exists, False otherwise.

        """
        return os.path.exists(file_path)

    def get_file_age(self, file_path: str) -> float:
        """Get file age in seconds.

        Args:
            file_path: The file path to check.

        Returns:
            File age in seconds since last modification.

        """
        return time.time() - os.path.getmtime(file_path)

    def remove_file(self, file_path: str) -> None:
        """Remove file safely.

        Args:
            file_path: The file path to remove.

        """
        try:
            os.remove(file_path)
        except OSError:
            pass

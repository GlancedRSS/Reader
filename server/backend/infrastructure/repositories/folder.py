"""Folder data access layer for folder operations."""

import logging
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Row, UnaryExpression, and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Subquery

from backend.domain.folder import CircularReferenceError
from backend.models import Feed, UserFeed, UserFolder

logger = logging.getLogger(__name__)


class FolderRepository:
    """Repository for folder database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the folder repository."""
        self.db = db

    @staticmethod
    def _get_feed_count_subquery() -> Subquery:
        """Create subquery for counting feeds per folder."""
        return (
            select(
                UserFeed.folder_id,
                func.count(UserFeed.id).label("count"),
            )
            .where(UserFeed.folder_id.isnot(None))
            .group_by(UserFeed.folder_id)
            .subquery()
        )

    async def get_folder_by_id_and_user(
        self, folder_id: UUID, user_id: UUID
    ) -> UserFolder | None:
        """Get folder by ID and user."""
        query = select(UserFolder).where(
            and_(
                UserFolder.id == folder_id,
                UserFolder.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_by_id(
        self, folder_id: UUID, user_id: UUID
    ) -> UserFolder | None:
        """Get folder by ID with user filtering (alias for get_folder_by_id_and_user)."""
        return await self.get_folder_by_id_and_user(folder_id, user_id)

    async def folder_name_exists(
        self,
        user_id: UUID,
        name: str,
        parent_id: UUID | None,
        exclude_folder_id: UUID | None = None,
    ) -> bool:
        """Check if a folder with the given name exists for the same parent."""
        query = select(UserFolder).where(
            and_(
                UserFolder.user_id == user_id,
                UserFolder.name == name,
                UserFolder.parent_id == parent_id,
            )
        )

        if exclude_folder_id:
            query = query.where(UserFolder.id != exclude_folder_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_subfolders_paginated(
        self,
        parent_id: UUID,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Any], int]:
        """Get subfolders with pagination."""
        subfolders_count_query = select(func.count(UserFolder.id)).where(
            and_(
                UserFolder.user_id == user_id,
                UserFolder.parent_id == parent_id,
            )
        )
        subfolders_total_result = await self.db.execute(subfolders_count_query)
        subfolders_total = subfolders_total_result.scalar() or 0

        feed_count_subq = self._get_feed_count_subquery()

        subfolders_query = (
            select(
                UserFolder.id,
                UserFolder.name,
                UserFolder.parent_id,
                UserFolder.is_pinned,
                UserFolder.depth,
                func.coalesce(feed_count_subq.c.count, 0).label("feed_count"),
            )
            .outerjoin(
                feed_count_subq,
                UserFolder.id == feed_count_subq.c.folder_id,
            )
            .where(
                and_(
                    UserFolder.user_id == user_id,
                    UserFolder.parent_id == parent_id,
                )
            )
            .order_by(UserFolder.is_pinned.desc(), UserFolder.name)
            .limit(limit)
            .offset(offset)
        )

        subfolders_result = await self.db.execute(subfolders_query)
        subfolders = subfolders_result.all()

        return list(subfolders), subfolders_total

    async def create_folder(
        self,
        user_id: UUID,
        name: str,
        parent_id: UUID | None = None,
    ) -> UserFolder:
        """Create a new folder."""
        folder = UserFolder(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
        )

        self.db.add(folder)
        await self.db.flush()
        await self.db.refresh(folder)
        return folder

    async def update_folder(
        self, folder_id: UUID, user_id: UUID, update_data: dict[str, Any]
    ) -> UserFolder:
        """Update folder."""
        folder = await self.get_folder_by_id_and_user(folder_id, user_id)
        if not folder:
            raise ValueError("Folder not found")

        for field, value in update_data.items():
            if hasattr(folder, field):
                setattr(folder, field, value)

        await self.db.flush()
        await self.db.refresh(folder)
        return folder

    async def delete_folder(self, folder_id: UUID, user_id: UUID) -> None:
        """Delete folder."""
        folder = await self.get_folder_by_id_and_user(folder_id, user_id)
        if not folder:
            raise ValueError("Folder not found")

        await self.db.delete(folder)

    async def get_folder_capacity_metrics(
        self, user_id: UUID, parent_id: UUID | None
    ) -> tuple[int, int]:
        """Get folder capacity metrics for validation."""
        if parent_id:
            depth_query = select(UserFolder.depth).where(
                and_(
                    UserFolder.id == parent_id,
                    UserFolder.user_id == user_id,
                )
            )
            result = await self.db.execute(depth_query)
            parent_depth = result.scalar() or 0
            new_depth = parent_depth + 1
        else:
            new_depth = 0

        if parent_id:
            count_query = select(func.count(UserFolder.id)).where(
                and_(
                    UserFolder.user_id == user_id,
                    UserFolder.parent_id == parent_id,
                )
            )
            result = await self.db.execute(count_query)
            folders_used = result.scalar() or 0
        else:
            count_query = select(func.count(UserFolder.id)).where(
                and_(
                    UserFolder.user_id == user_id,
                    UserFolder.parent_id.is_(None),
                )
            )
            result = await self.db.execute(count_query)
            folders_used = result.scalar() or 0

        return folders_used, new_depth

    async def check_circular_reference(
        self, folder_id: UUID, new_parent_id: UUID, user_id: UUID
    ) -> None:
        """Check for circular references in folder hierarchy."""
        circular_query = text(
            """
            WITH RECURSIVE folder_tree AS (
                SELECT id, parent_id FROM personalization.user_folders
                WHERE id = :folder_id AND user_id = :user_id

                UNION ALL

                SELECT f.id, f.parent_id FROM personalization.user_folders f
                JOIN folder_tree ft ON f.parent_id = ft.id
                WHERE f.user_id = :user_id
            )
            SELECT 1 FROM folder_tree WHERE id = :new_parent_id
        """
        )

        result = await self.db.execute(
            circular_query,
            {
                "folder_id": folder_id,
                "new_parent_id": new_parent_id,
                "user_id": user_id,
            },
        )
        if result.scalar():
            raise CircularReferenceError(
                "Circular reference detected in folder hierarchy"
            )

    async def get_recursive_unread_counts(
        self, user_id: UUID
    ) -> dict[UUID, int]:
        """Get recursive unread counts for all user folders."""
        try:
            folders_query = text(
                """
                WITH RECURSIVE folder_hierarchy AS (
                    SELECT
                        id,
                        parent_id,
                        ARRAY[id] as path
                    FROM personalization.user_folders
                    WHERE user_id = :user_id AND parent_id IS NULL

                    UNION ALL

                    SELECT
                        f.id,
                        f.parent_id,
                        fh.path || f.id
                    FROM personalization.user_folders f
                    JOIN folder_hierarchy fh ON f.parent_id = fh.id
                    WHERE f.user_id = :user_id
                )
                SELECT
                    id,
                    parent_id,
                    path
                FROM folder_hierarchy
                ORDER BY array_length(path, 1)
            """
            )

            folders_result = await self.db.execute(
                folders_query, {"user_id": user_id}
            )
            folders = folders_result.fetchall()

            if not folders:
                return {}

            feed_counts_stmt = (
                select(
                    UserFeed.folder_id,
                    func.coalesce(func.sum(UserFeed.unread_count), 0).label(
                        "unread_count"
                    ),
                )
                .where(
                    and_(
                        UserFeed.folder_id.isnot(None),
                        UserFeed.user_id == user_id,
                    )
                )
                .group_by(UserFeed.folder_id)
            )

            feed_counts_result = await self.db.execute(feed_counts_stmt)
            direct_counts = {
                row.folder_id: row.unread_count
                for row in feed_counts_result.all()
            }

            recursive_counts = {}
            for folder in folders:
                folder_id = folder.id
                recursive_counts[folder_id] = direct_counts.get(folder_id, 0)

            folders_sorted_by_depth = sorted(
                folders, key=lambda f: len(f.path), reverse=True
            )

            for folder in folders_sorted_by_depth:
                if folder.parent_id:
                    parent_count = recursive_counts.get(folder.id, 0)
                    current_parent_count = recursive_counts.get(
                        folder.parent_id, 0
                    )
                    recursive_counts[folder.parent_id] = (
                        current_parent_count + parent_count
                    )

            return recursive_counts

        except Exception as e:
            logger.warning(
                "Recursive CTE failed for unread counts, falling back to simple counts: %s",
                e,
            )
            feed_stmt = (
                select(
                    UserFeed.folder_id,
                    func.coalesce(func.sum(UserFeed.unread_count), 0).label(
                        "unread_count"
                    ),
                )
                .where(
                    and_(
                        UserFeed.folder_id.isnot(None),
                        UserFeed.user_id == user_id,
                    )
                )
                .group_by(UserFeed.folder_id)
            )

            feed_result = await self.db.execute(feed_stmt)
            return {
                row.folder_id: row.unread_count for row in feed_result.all()
            }

    async def get_folder_details_with_feed_count(
        self, folder_id: UUID, user_id: UUID
    ) -> Row[Any] | None:
        """Get folder details with feed count."""
        feed_count_subq = self._get_feed_count_subquery()

        stmt = (
            select(
                UserFolder.id,
                UserFolder.name,
                UserFolder.parent_id,
                UserFolder.is_pinned,
                UserFolder.depth,
                func.coalesce(feed_count_subq.c.count, 0).label("feed_count"),
            )
            .outerjoin(
                feed_count_subq,
                UserFolder.id == feed_count_subq.c.folder_id,
            )
            .where(
                and_(
                    UserFolder.id == folder_id,
                    UserFolder.user_id == user_id,
                )
            )
        )

        result = await self.db.execute(stmt)
        return result.first()

    async def get_all_feeds_for_user(
        self, user_id: UUID, sort_order: str | None = None
    ) -> Sequence[Row[Any]]:
        """Get all feeds for the user with folder association."""
        secondary_sort: UnaryExpression[Any]
        if sort_order == "recent_first":
            secondary_sort = Feed.last_update.desc().nullslast()
        else:  # alphabetical or default
            secondary_sort = UserFeed.title.asc()

        stmt = (
            select(
                UserFeed.id,
                UserFeed.feed_id,
                UserFeed.title,
                UserFeed.unread_count,
                UserFeed.is_pinned,
                UserFeed.is_active,
                UserFeed.folder_id,
                Feed.website,
            )
            .join(Feed, UserFeed.feed_id == Feed.id)
            .where(UserFeed.user_id == user_id)
            .order_by(UserFeed.is_pinned.desc(), secondary_sort)
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def get_all_folders_for_user(
        self, user_id: UUID
    ) -> Sequence[Row[Any]]:
        """Get all folders for the user in a single query."""
        feed_count_subq = self._get_feed_count_subquery()

        stmt = (
            select(
                UserFolder.id,
                UserFolder.name,
                UserFolder.parent_id,
                UserFolder.is_pinned,
                UserFolder.depth,
                func.coalesce(feed_count_subq.c.count, 0).label("feed_count"),
            )
            .outerjoin(
                feed_count_subq,
                UserFolder.id == feed_count_subq.c.folder_id,
            )
            .where(UserFolder.user_id == user_id)
            .order_by(
                UserFolder.depth, UserFolder.is_pinned.desc(), UserFolder.name
            )
        )

        result = await self.db.execute(stmt)
        return result.all()

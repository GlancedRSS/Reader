"""Application service for folder operations."""

import logging
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundError, ValidationError
from backend.domain.folder import (
    CircularReferenceError,
    FolderDepthExceededError,
    FolderLimitExceededError,
    FolderValidationDomain,
)
from backend.infrastructure.repositories import FolderRepository
from backend.schemas.core import (
    PaginationMetadata,
    ResponseMessage,
)
from backend.schemas.domain import (
    FeedInFolderResponse,
    FolderCreateRequest,
    FolderListResponse,
    FolderResponse,
    FolderTreeResponse,
    FolderUpdateRequest,
)

logger = logging.getLogger(__name__)


class FolderApplication:
    """Application service for folder operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the folder application with database session."""
        self.db = db
        self.repository = FolderRepository(db)

    @staticmethod
    def _calculate_total_feed_count(folder_row: Row[Any]) -> int:
        """Calculate total feed count from folder row."""
        return folder_row.feed_count or 0

    async def get_folder_details(
        self,
        folder_id: UUID,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> FolderResponse:
        """Get folder details with paginated subfolders."""
        folder_details = (
            await self.repository.get_folder_details_with_feed_count(
                folder_id, user_id
            )
        )
        if not folder_details:
            raise NotFoundError("Folder not found")

        (
            subfolders,
            subfolders_total,
        ) = await self.repository.get_subfolders_paginated(
            folder_id, user_id, limit, offset
        )

        recursive_unread_counts = (
            await self.repository.get_recursive_unread_counts(user_id)
        )

        subfolder_responses = [
            FolderListResponse(
                id=subfolder.id,
                name=subfolder.name,
                parent_id=subfolder.parent_id,
                feed_count=self._calculate_total_feed_count(subfolder),
                unread_count=recursive_unread_counts.get(subfolder.id, 0),
                is_pinned=subfolder.is_pinned,
                depth=subfolder.depth or 0,
            )
            for subfolder in subfolders
        ]

        has_more = offset + limit < subfolders_total
        pagination = PaginationMetadata(
            total=subfolders_total,
            limit=limit,
            offset=offset,
            has_more=has_more,
            next_cursor=None,
        )

        return FolderResponse(
            id=folder_details.id,
            name=folder_details.name,
            parent_id=folder_details.parent_id,
            feed_count=self._calculate_total_feed_count(folder_details),
            unread_count=recursive_unread_counts.get(folder_id, 0),
            is_pinned=folder_details.is_pinned,
            depth=folder_details.depth or 0,
            data=subfolder_responses,
            pagination=pagination.model_dump(),
        )

    async def create_folder(
        self,
        folder_data: FolderCreateRequest,
        user_id: UUID,
    ) -> FolderListResponse:
        """Create a new folder."""
        try:
            FolderValidationDomain.validate_folder_name(folder_data.name)

            (
                folders_used,
                depth,
            ) = await self.repository.get_folder_capacity_metrics(
                user_id, folder_data.parent_id
            )
            FolderValidationDomain.validate_folder_capacity(folders_used, depth)
        except (FolderDepthExceededError, FolderLimitExceededError) as e:
            raise ValidationError(str(e)) from e

        name_exists = await self.repository.folder_name_exists(
            user_id, folder_data.name, folder_data.parent_id
        )
        if name_exists:
            raise ValidationError("Folder with this name already exists")

        if folder_data.parent_id:
            parent_folder = await self.repository.get_folder_by_id_and_user(
                folder_data.parent_id, user_id
            )
            if not parent_folder:
                raise ValidationError("Invalid parent folder")

        try:
            folder = await self.repository.create_folder(
                user_id, folder_data.name, folder_data.parent_id
            )
        except CircularReferenceError as e:
            raise ValidationError(str(e)) from e

        return FolderListResponse(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            feed_count=0,
            unread_count=0,
            is_pinned=folder.is_pinned,
            depth=folder.depth or 0,
        )

    async def update_folder(
        self,
        folder_id: UUID,
        folder_data: FolderUpdateRequest,
        user_id: UUID,
    ) -> ResponseMessage:
        """Update folder."""
        folder = await self.repository.get_folder_by_id_and_user(
            folder_id, user_id
        )
        if not folder:
            raise NotFoundError("Folder not found")

        update_data = folder_data.model_dump(exclude_unset=True)

        if "name" in update_data or "parent_id" in update_data:
            new_name = update_data.get("name", folder.name)
            new_parent_id = update_data.get("parent_id", folder.parent_id)

            if new_name or new_parent_id:
                name_exists = await self.repository.folder_name_exists(
                    user_id,
                    new_name,
                    new_parent_id,
                    exclude_folder_id=folder_id,
                )
                if name_exists:
                    raise ValidationError(
                        "Folder with this name already exists"
                    )

        if "parent_id" in update_data:
            new_parent_id = update_data["parent_id"]
            if new_parent_id and new_parent_id == folder_id:
                raise ValidationError("Folder cannot be its own parent")

            if new_parent_id:
                try:
                    await self.repository.check_circular_reference(
                        folder_id, new_parent_id, user_id
                    )
                except CircularReferenceError as e:
                    raise ValidationError(str(e)) from e

            if new_parent_id:
                parent_folder = await self.repository.get_folder_by_id_and_user(
                    new_parent_id, user_id
                )
                if not parent_folder:
                    raise ValidationError("Invalid parent folder")

                try:
                    (
                        folders_used,
                        depth,
                    ) = await self.repository.get_folder_capacity_metrics(
                        user_id, new_parent_id
                    )
                    FolderValidationDomain.validate_folder_capacity(
                        folders_used, depth
                    )
                except (
                    FolderDepthExceededError,
                    FolderLimitExceededError,
                ) as e:
                    raise ValidationError(str(e)) from e

        await self.repository.update_folder(folder_id, user_id, update_data)

        return ResponseMessage(message="Folder updated successfully")

    async def delete_folder(
        self, folder_id: UUID, user_id: UUID
    ) -> ResponseMessage:
        """Delete folder."""
        folder = await self.repository.get_folder_by_id_and_user(
            folder_id, user_id
        )
        if not folder:
            raise NotFoundError("Folder not found")

        await self.repository.delete_folder(folder_id, user_id)

        return ResponseMessage(message="Folder deleted successfully")

    async def get_folder_tree(
        self, user_id: UUID, max_depth: int = 3
    ) -> list[FolderTreeResponse]:
        """Get complete folder hierarchy with feeds."""
        from sqlalchemy import select

        from backend.models import UserPreferences

        prefs_query = select(UserPreferences).where(
            UserPreferences.user_id == user_id
        )
        prefs_result = await self.db.execute(prefs_query)
        user_prefs = prefs_result.scalar_one_or_none()
        feed_sort_order = (
            user_prefs.feed_sort_order if user_prefs else "recent_first"
        )

        all_folders = await self.repository.get_all_folders_for_user(user_id)

        recursive_unread_counts = (
            await self.repository.get_recursive_unread_counts(user_id)
        )

        all_feeds = await self.repository.get_all_feeds_for_user(
            user_id, sort_order=feed_sort_order
        )
        feeds_by_folder_id: dict[UUID | None, list[Row[Any]]] = {}
        for feed in all_feeds:
            if feed.folder_id not in feeds_by_folder_id:
                feeds_by_folder_id[feed.folder_id] = []
            feeds_by_folder_id[feed.folder_id].append(feed)

        folder_tree_responses = self._build_tree_in_memory(
            all_folders,
            recursive_unread_counts,
            feeds_by_folder_id,
            max_depth,
            user_id,
        )

        orphan_feeds = feeds_by_folder_id.get(None, [])
        orphan_feed_responses = [
            self._map_feed_to_response(feed) for feed in orphan_feeds
        ]

        if orphan_feed_responses:
            folder_tree_responses.append(
                FolderTreeResponse(
                    id=None,
                    name="Uncategorized",
                    parent_id=None,
                    feed_count=len(orphan_feed_responses),
                    unread_count=sum(
                        f.unread_count for f in orphan_feed_responses
                    ),
                    is_pinned=False,
                    depth=0,
                    feeds=orphan_feed_responses,
                    subfolders=[],
                )
            )

        return folder_tree_responses

    def _build_tree_in_memory(
        self,
        all_folders: Sequence[Row[Any]],
        recursive_unread_counts: dict[UUID, int],
        feeds_by_folder_id: dict[UUID | None, list[Row[Any]]],
        max_depth: int,
        user_id: UUID,
    ) -> list[FolderTreeResponse]:
        """Build folder tree in-memory from flat folder list."""
        children_by_parent: dict[UUID | None, list[Row[Any]]] = {}
        for folder in all_folders:
            parent_id = folder.parent_id
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = []
            children_by_parent[parent_id].append(folder)

        def build_folder_node(folder: Row[Any]) -> FolderTreeResponse:
            feeds = feeds_by_folder_id.get(folder.id, [])
            feed_responses = [
                self._map_feed_to_response(feed) for feed in feeds
            ]

            subfolders = []
            folder_depth = folder.depth or 0
            if folder_depth + 1 < max_depth:
                child_folders = children_by_parent.get(folder.id, [])
                for child in child_folders:
                    subfolders.append(build_folder_node(child))

            return FolderTreeResponse(
                id=folder.id,
                name=folder.name,
                parent_id=folder.parent_id,
                feed_count=self._calculate_total_feed_count(folder),
                unread_count=recursive_unread_counts.get(folder.id, 0),
                is_pinned=folder.is_pinned,
                depth=folder_depth,
                feeds=feed_responses,
                subfolders=subfolders,
            )

        root_folders = children_by_parent.get(None, [])

        folder_ids = {folder.id for folder in all_folders}
        orphaned_folders = [
            folder
            for folder in all_folders
            if folder.parent_id is not None
            and folder.parent_id not in folder_ids
        ]

        if orphaned_folders:
            logger.warning(
                "Found %d folders with orphaned parent_id for user %s. "
                "Including at root level.",
                len(orphaned_folders),
                user_id,
            )
            root_folders.extend(orphaned_folders)

        return [build_folder_node(folder) for folder in root_folders]

    @staticmethod
    def _map_feed_to_response(feed: Row[Any]) -> FeedInFolderResponse:
        """Map a feed row to FeedInFolderResponse."""
        return FeedInFolderResponse(
            id=feed.id,
            title=feed.title,
            unread_count=feed.unread_count,
            website=feed.website,
            is_pinned=feed.is_pinned,
            is_active=feed.is_active,
        )

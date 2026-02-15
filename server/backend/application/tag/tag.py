"""Application service for tag management and article-tag relationships."""

from typing import TYPE_CHECKING
from uuid import UUID

import structlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from backend.domain.tag import TagValidationDomain
from backend.infrastructure.repositories import UserTagRepository

if TYPE_CHECKING:
    from backend.models import UserTag
from backend.domain import DEFAULT_LIMIT
from backend.schemas.core import (
    PaginatedResponse,
    PaginationMetadata,
    ResponseMessage,
)
from backend.schemas.domain import (
    TagCreateRequest,
    TagListResponse,
    TagUpdateRequest,
)

logger = structlog.get_logger(__name__)


class TagApplication:
    """Application service for tag management and article-tag relationships."""

    def __init__(self, db: AsyncSession):
        """Initialize the tag application with database session.

        Args:
            db: Async database session for repository operations.

        """
        self.db = db

        self.repository = UserTagRepository(db)

    @staticmethod
    def _build_tag_response(tag: "UserTag") -> TagListResponse:
        """Build TagListResponse from tag model.

        Args:
            tag: Tag model instance.

        Returns:
            TagListResponse.

        """
        return TagListResponse(
            id=tag.id,
            name=tag.name,
            article_count=tag.article_count,
        )

    async def get_user_tag(
        self, user_id: UUID, tag_id: UUID
    ) -> TagListResponse:
        """Get a specific tag for a user.

        Args:
            user_id: The ID of the user.
            tag_id: The ID of the tag.

        Returns:
            Tag response.

        Raises:
            NotFoundError: If tag is not found.

        """
        tag = await self.repository.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundError("Tag not found")

        return self._build_tag_response(tag)

    async def get_user_tags(
        self,
        user_id: UUID,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[TagListResponse]:
        """Get tags for a user with pagination.

        Args:
            user_id: The ID of the user.
            limit: Maximum number of tags to return.
            offset: Number of tags to skip.

        Returns:
            Paginated response containing user's tags.

        """
        tags, total = await self.repository.get_user_tags_paginated(
            user_id, limit, offset
        )

        tag_responses = [self._build_tag_response(tag) for tag in tags]

        has_more = offset + len(tag_responses) < total

        return PaginatedResponse(
            data=tag_responses,
            pagination=PaginationMetadata(
                total=total,
                limit=limit,
                offset=offset,
                has_more=has_more,
                next_cursor=str(offset + limit) if has_more else None,
            ),
        )

    async def create_user_tag(
        self, user_id: UUID, tag_data: TagCreateRequest
    ) -> TagListResponse:
        """Create a new user tag with validation and business rules.

        Args:
            user_id: The ID of the user creating the tag.
            tag_data: The tag creation request with name.

        Returns:
            Created or existing tag response.

        Raises:
            ValidationError: If tag validation fails.

        """
        try:
            sanitized_name = TagValidationDomain.validate_tag_name(
                tag_data.name
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e

        existing_tag = await self.repository.find_by_user_and_name(
            user_id, sanitized_name
        )
        if existing_tag:
            return self._build_tag_response(existing_tag)

        try:
            new_tag = await self.repository.create_tag(
                user_id=user_id,
                name=sanitized_name,
            )
            return self._build_tag_response(new_tag)
        except IntegrityError:
            tag = await self.repository.find_by_user_and_name(
                user_id, sanitized_name
            )
            if tag:
                return self._build_tag_response(tag)
            logger.exception(
                "IntegrityError on tag create but tag not found",
                user_id=str(user_id),
                name=sanitized_name,
            )
            raise

    async def update_user_tag(
        self, user_id: UUID, tag_id: UUID, tag_data: TagUpdateRequest
    ) -> ResponseMessage:
        """Update a user tag with validation.

        Args:
            user_id: The ID of the user.
            tag_id: The ID of the tag to update.
            tag_data: The tag update request.

        Returns:
            Response message indicating successful update.

        Raises:
            NotFoundError: If tag is not found.
            ValidationError: If tag validation fails.
            ConflictError: If tag name already exists for another tag.

        """
        tag = await self.repository.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundError("Tag not found")

        try:
            sanitized_name = TagValidationDomain.validate_tag_update(
                name=tag_data.name,
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e

        update_data = tag_data.model_dump(exclude_unset=True)
        if sanitized_name is not None:
            update_data["name"] = sanitized_name

        try:
            await self.repository.update_tag(tag, update_data)
        except IntegrityError:
            raise ConflictError(
                f"Tag '{sanitized_name}' already exists"
            ) from None

        return ResponseMessage(message="Tag updated successfully")

    async def delete_user_tag(
        self, user_id: UUID, tag_id: UUID
    ) -> ResponseMessage:
        """Delete a user tag with business rule validation.

        Args:
            user_id: The ID of the user.
            tag_id: The ID of the tag to delete.

        Returns:
            Response message indicating successful deletion.

        Raises:
            NotFoundError: If tag is not found.

        """
        tag = await self.repository.find_by_id(tag_id, user_id)
        if not tag:
            raise NotFoundError("Tag not found")

        await self.repository.delete_tag(tag)

        return ResponseMessage(message="Tag deleted successfully")

    async def sync_article_tags(
        self, user_id: UUID, article_id: UUID, desired_tag_ids: list[UUID]
    ) -> dict[str, list[UUID]]:
        """Sync article tags to match desired state.

        Adds tags that are in desired list but not current,
        and removes tags that are current but not in desired.

        Args:
            user_id: The ID of the user (for access control).
            article_id: The article to sync tags for.
            desired_tag_ids: The desired tag IDs.

        Returns:
            Dictionary with 'added' and 'removed' tag lists.

        Raises:
            NotFoundError: If user doesn't have access to the article.
            ValueError: If user doesn't own all tags in desired_tag_ids.

        """
        current_tags = await self.repository.get_article_tags(
            article_id, user_id
        )

        tags_to_add = [
            tag_id for tag_id in desired_tag_ids if tag_id not in current_tags
        ]
        tags_to_remove = [
            tag_id for tag_id in current_tags if tag_id not in desired_tag_ids
        ]

        added = []
        removed = []

        if tags_to_add:
            added = await self.repository.add_tags_to_article(
                article_id, tags_to_add, user_id
            )

        if tags_to_remove:
            removed = await self.repository.remove_tags_from_article(
                article_id, tags_to_remove, user_id
            )

        return {"added": added, "removed": removed}

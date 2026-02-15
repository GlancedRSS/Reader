"""Tag data access layer for tag and article-tag relationship operations."""

from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import ArticleTag, UserArticle, UserTag

logger = structlog.get_logger(__name__)


class UserTagRepository:
    """Repository for tag and article-tag relationship database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the tag repository.

        Args:
            db: Async database session.

        """
        self.db = db

    async def find_by_user_and_name(
        self, user_id: UUID, name: str
    ) -> UserTag | None:
        """Find a tag by user and name.

        Args:
            user_id: The user ID.
            name: The tag name.

        Returns:
            The UserTag if found, None otherwise.

        """
        query = select(UserTag).where(
            (UserTag.user_id == user_id) & (UserTag.name == name)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_by_id(self, tag_id: UUID, user_id: UUID) -> UserTag | None:
        """Find a tag by ID and user.

        Args:
            tag_id: The tag ID.
            user_id: The user ID.

        Returns:
            The Tag if found, None otherwise.

        """
        query = select(UserTag).where(
            (UserTag.id == tag_id) & (UserTag.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_tags(self, user_id: UUID) -> list[UserTag]:
        """Get tags for a user.

        Args:
            user_id: The user ID.

        Returns:
            List of Tag objects ordered by name.

        """
        query = select(UserTag).where(UserTag.user_id == user_id)
        query = query.order_by(UserTag.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_tags_paginated(
        self, user_id: UUID, limit: int, offset: int
    ) -> tuple[list[UserTag], int]:
        """Get tags for a user with pagination.

        Args:
            user_id: The user ID.
            limit: Maximum number of tags to return.
            offset: Number of tags to skip.

        Returns:
            Tuple of (list of Tag objects, total count).

        """
        count_query = select(func.count(UserTag.id)).where(
            UserTag.user_id == user_id
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = select(UserTag).where(UserTag.user_id == user_id)
        query = query.order_by(UserTag.name)
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        tags = list(result.scalars().all())

        return tags, total

    async def create_tag(
        self,
        user_id: UUID,
        name: str,
    ) -> UserTag:
        """Create a new tag.

        Args:
            user_id: The user ID.
            name: The tag name.

        Returns:
            The created Tag.

        """
        tag = UserTag(
            user_id=user_id,
            name=name,
        )
        self.db.add(tag)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def update_tag(
        self, tag: UserTag, update_data: dict[str, Any]
    ) -> None:
        """Update an existing tag.

        Args:
            tag: The Tag to update.
            update_data: Dictionary of fields to update.

        """
        for field, value in update_data.items():
            if hasattr(tag, field):
                setattr(tag, field, value)

        await self.db.flush()

    async def delete_tag(self, tag: UserTag) -> None:
        """Delete a tag (CASCADE will handle ArticleTag entries).

        Args:
            tag: The Tag to delete.

        """
        await self.db.delete(tag)
        await self.db.flush()

    async def get_or_create_tag(self, user_id: UUID, name: str) -> UserTag:
        """Get or create a tag.

        Args:
            user_id: The user ID.
            name: The tag name.

        Returns:
            The existing or newly created Tag.

        """
        existing = await self.find_by_user_and_name(user_id, name)
        if existing:
            return existing

        return await self.create_tag(user_id, name)

    async def get_article_tags(
        self, article_id: UUID, user_id: UUID
    ) -> list[UUID]:
        """Get all tag IDs for an article, filtered by user.

        Args:
            article_id: The article ID.
            user_id: The user ID.

        Returns:
            List of tag IDs belonging to the user.

        """
        user_article_query = select(UserArticle.id).where(
            (UserArticle.user_id == user_id)
            & (UserArticle.article_id == article_id)
        )
        user_article_result = await self.db.execute(user_article_query)
        user_article_id = user_article_result.scalar_one_or_none()

        if not user_article_id:
            return []

        query = (
            select(ArticleTag.user_tag_id)
            .join(UserTag, ArticleTag.user_tag_id == UserTag.id)
            .where(
                (ArticleTag.user_article_id == user_article_id)
                & (UserTag.user_id == user_id)
            )
        )
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def add_tags_to_article(
        self, article_id: UUID, tag_ids: list[UUID], user_id: UUID
    ) -> list[UUID]:
        """Add multiple tags to an article, filtered by user.

        Args:
            article_id: The article ID.
            tag_ids: List of tag IDs to add.
            user_id: The user ID.

        Returns:
            List of tag IDs that were actually added (excluding existing relationships).

        Raises:
            ValueError: If any tag does not belong to the user.

        """
        added_tags = []

        try:
            tags_query = select(UserTag.id).where(
                (UserTag.id.in_(tag_ids)) & (UserTag.user_id == user_id)
            )
            tags_result = await self.db.execute(tags_query)
            owned_tag_ids = {row[0] for row in tags_result.all()}

            if len(owned_tag_ids) != len(tag_ids):
                raise ValueError("One or more tags not found or access denied")

            user_article_query = select(UserArticle.id).where(
                (UserArticle.user_id == user_id)
                & (UserArticle.article_id == article_id)
            )
            user_article_result = await self.db.execute(user_article_query)
            user_article_id = user_article_result.scalar_one_or_none()

            if not user_article_id:
                raise ValueError("Article not found for user")

            existing_query = select(ArticleTag.user_tag_id).where(
                (ArticleTag.user_article_id == user_article_id)
                & (ArticleTag.user_tag_id.in_(tag_ids))
            )
            existing_result = await self.db.execute(existing_query)
            existing_tag_ids = {row[0] for row in existing_result.all()}

            for tag_id in tag_ids:
                if tag_id not in existing_tag_ids:
                    article_tag = ArticleTag(
                        user_article_id=user_article_id, user_tag_id=tag_id
                    )
                    self.db.add(article_tag)
                    added_tags.append(tag_id)

            if added_tags:
                await self.db.flush()
                logger.debug(
                    "Added tags to article",
                    article_id=article_id,
                    user_id=str(user_id),
                    added_tag_count=len(added_tags),
                )

            return added_tags

        except ValueError:
            raise
        except Exception as e:
            logger.exception(
                "Error adding tags to article",
                article_id=article_id,
                user_id=str(user_id),
                tag_ids=tag_ids,
                error=str(e),
            )
            raise

    async def remove_tags_from_article(
        self, article_id: UUID, tag_ids: list[UUID], user_id: UUID
    ) -> list[UUID]:
        """Remove multiple tags from an article, filtered by user.

        Args:
            article_id: The article ID.
            tag_ids: List of tag IDs to remove.
            user_id: The user ID.

        Returns:
            List of tag IDs that were actually removed.

        """
        if not tag_ids:
            return []

        try:
            user_article_query = select(UserArticle.id).where(
                (UserArticle.user_id == user_id)
                & (UserArticle.article_id == article_id)
            )
            user_article_result = await self.db.execute(user_article_query)
            user_article_id = user_article_result.scalar_one_or_none()

            if not user_article_id:
                return []

            existing_query = (
                select(ArticleTag.user_tag_id)
                .join(UserTag, ArticleTag.user_tag_id == UserTag.id)
                .where(
                    (ArticleTag.user_article_id == user_article_id)
                    & (ArticleTag.user_tag_id.in_(tag_ids))
                    & (UserTag.user_id == user_id)
                )
            )
            existing_result = await self.db.execute(existing_query)
            existing_tag_ids = {row[0] for row in existing_result.all()}

            delete_stmt = (
                delete(ArticleTag)
                .where(
                    (ArticleTag.user_article_id == user_article_id)
                    & (ArticleTag.user_tag_id.in_(tag_ids))
                )
                .where(
                    ArticleTag.user_tag_id.in_(
                        select(UserTag.id).where(UserTag.user_id == user_id)
                    )
                )
            )
            result = await self.db.execute(delete_stmt)
            removed_count = result.rowcount

            if removed_count > 0:
                await self.db.flush()
                logger.debug(
                    "Removed tags from article",
                    article_id=article_id,
                    user_id=str(user_id),
                    removed_count=removed_count,
                )

            return [tid for tid in tag_ids if tid in existing_tag_ids]

        except Exception as e:
            logger.exception(
                "Error removing tags from article",
                article_id=article_id,
                user_id=str(user_id),
                tag_ids=tag_ids,
                error=str(e),
            )
            raise

    async def remove_articles_from_all_tags(
        self, article_ids: list[UUID], user_id: UUID
    ) -> int:
        """Remove multiple articles from all tags efficiently, filtered by user.

        Args:
            article_ids: List of article IDs to remove from all tags.
            user_id: The user ID.

        Returns:
            The number of relationships removed.

        """
        if not article_ids:
            return 0

        try:
            logger.info(
                "Starting bulk removal of articles from tags",
                article_count=len(article_ids),
                user_id=str(user_id),
            )

            user_articles_query = select(UserArticle.id).where(
                (UserArticle.user_id == user_id)
                & (UserArticle.article_id.in_(article_ids))
            )
            user_articles_result = await self.db.execute(user_articles_query)
            user_article_ids = [row[0] for row in user_articles_result.all()]

            if not user_article_ids:
                return 0

            delete_stmt = (
                delete(ArticleTag)
                .where(ArticleTag.user_article_id.in_(user_article_ids))
                .where(
                    ArticleTag.user_tag_id.in_(
                        select(UserTag.id).where(UserTag.user_id == user_id)
                    )
                )
            )
            result = await self.db.execute(delete_stmt)
            deleted_count = result.rowcount

            logger.info(
                "Successfully removed multiple articles from all tags",
                article_count=len(article_ids),
                user_id=str(user_id),
                relationships_removed=deleted_count,
            )

            await self.db.flush()
            return deleted_count

        except Exception as e:
            logger.exception(
                "Error removing multiple articles from tags",
                article_count=len(article_ids),
                user_id=str(user_id),
                error=str(e),
            )
            raise

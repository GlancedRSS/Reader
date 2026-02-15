"""UserTag model for user-defined tags."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.article_tag import ArticleTag


class UserTag(Base):
    """User-defined tag model for categorizing articles."""

    __tablename__ = "user_tags"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_tag_name"),
        CheckConstraint(
            "article_count >= 0",
            name="chk_personalization_user_tags_article_count",
        ),
        Index("idx_personalization_user_tags_name", "name"),
        Index("idx_personalization_user_tags_user_id", "user_id"),
        Index(
            "idx_personalization_user_tags_user_name_optimized",
            "user_id",
            "name",
            postgresql_where=sa_text("name IS NOT NULL"),
        ),
        {"schema": "personalization"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        primary_key=True,
        server_default=sa_text("extensions.gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        ForeignKey("accounts.users.id", ondelete="CASCADE"),
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    article_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )

    article_relations: Mapped[list["ArticleTag"]] = relationship(
        "ArticleTag", back_populates="tag", passive_deletes=True
    )

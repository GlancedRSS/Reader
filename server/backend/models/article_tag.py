"""ArticleTag model for junction table linking articles to user tags."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.user_article import UserArticle
    from backend.models.user_tag import UserTag


class ArticleTag(Base):
    """Junction table linking articles to user tags."""

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("user_article_id", "user_tag_id"),
        Index("idx_personalization_tags_user_article_id", "user_article_id"),
        Index("idx_personalization_tags_user_tag_id", "user_tag_id"),
        Index(
            "idx_personalization_tags_user_tag_filter",
            "user_tag_id",
            postgresql_include=sa_text("user_article_id"),
        ),
        {"schema": "personalization"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        primary_key=True,
        server_default=sa_text("extensions.gen_random_uuid()"),
    )
    user_article_id: Mapped[UUID] = mapped_column(
        ForeignKey("content.user_articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_tag_id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        ForeignKey("personalization.user_tags.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )

    user_article: Mapped["UserArticle"] = relationship(
        "UserArticle", back_populates="tags"
    )
    tag: Mapped["UserTag"] = relationship(
        "UserTag", back_populates="article_relations"
    )

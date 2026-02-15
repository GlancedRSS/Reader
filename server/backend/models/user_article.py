"""UserArticle model for user-specific article states (read/unread, read later)."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.article import Article
    from backend.models.article_tag import ArticleTag


class UserArticle(Base):
    """User-specific article states (read status, read later, etc.)."""

    __tablename__ = "user_articles"
    __table_args__ = (
        Index("idx_content_user_articles_article_id", "article_id"),
        Index(
            "idx_content_user_articles_user_read",
            "user_id",
            "is_read",
            postgresql_where=sa_text("is_read = false"),
        ),
        Index(
            "idx_content_user_articles_read_later",
            "user_id",
            "read_later",
            postgresql_where=sa_text("read_later = true"),
        ),
        UniqueConstraint("user_id", "article_id"),
        {"schema": "content"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        primary_key=True,
        server_default=sa_text("extensions.gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        ForeignKey("accounts.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    article_id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        ForeignKey("content.articles.id", ondelete="CASCADE"),
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    read_later: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )

    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="user_articles",
    )
    tags: Mapped[list["ArticleTag"]] = relationship(
        "ArticleTag",
        back_populates="user_article",
        cascade="all, delete-orphan",
    )

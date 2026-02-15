"""Feed model for unified feed definitions (RSS/Atom feeds)."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.article_source import ArticleSource
    from backend.models.user_feed import UserFeed


class Feed(Base):
    """Unified feed definitions for RSS/Atom feeds."""

    __tablename__ = "feeds"
    __table_args__ = (
        CheckConstraint(
            "length(title) <= 500",
            name="chk_content_feeds_title_length",
        ),
        CheckConstraint(
            "length(description) <= 2000",
            name="chk_content_feeds_description_length",
        ),
        CheckConstraint(
            "feed_type IN ('rss', 'atom')",
            name="chk_content_feeds_feed_type",
        ),
        CheckConstraint(
            "language IS NULL OR language ~ '^[a-z]{2}(-[A-Z]{2})?$'",
            name="chk_content_feeds_language",
        ),
        CheckConstraint(
            "website IS NULL OR public.is_valid_url(website)",
            name="chk_content_feeds_website",
        ),
        CheckConstraint(
            "canonical_url IS NULL OR public.is_valid_url(canonical_url)",
            name="chk_content_feeds_canonical_url",
        ),
        CheckConstraint(
            "error_count >= 0",
            name="chk_content_feeds_error_count",
        ),
        CheckConstraint(
            "last_error IS NULL OR length(last_error) <= 2000",
            name="chk_content_feeds_last_error_length",
        ),
        Index(
            "idx_content_feeds_canonical_url_unique",
            "canonical_url",
            postgresql_where=sa_text("canonical_url IS NOT NULL"),
        ),
        Index(
            "idx_content_feeds_last_fetched_at",
            "last_fetched_at",
        ),
        Index(
            "idx_content_feeds_last_update_desc",
            sa_text("last_update DESC NULLS LAST"),
        ),
        Index(
            "idx_content_feeds_latest_articles",
            "latest_articles",
            postgresql_using="gin",
        ),
        Index(
            "idx_content_feeds_error_count",
            sa_text("error_count"),
            postgresql_where=sa_text("error_count > 0"),
        ),
        Index(
            "idx_content_feeds_active_type",
            "is_active",
            "feed_type",
            postgresql_where=sa_text("is_active = true"),
        ),
        {"schema": "content"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        primary_key=True,
        server_default=sa_text("extensions.gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    feed_type: Mapped[str] = mapped_column(Text, default="rss", nullable=False)
    canonical_url: Mapped[str | None] = mapped_column(Text)

    language: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(Text)

    latest_articles: Mapped[list[UUID]] = mapped_column(
        ARRAY(PostgresUUID), default=list
    )
    last_update: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    last_fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    last_error_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
        onupdate=sa_text("NOW()"),
    )

    sources: Mapped[list["ArticleSource"]] = relationship(
        "ArticleSource",
        back_populates="feed",
    )
    user_subscriptions: Mapped[list["UserFeed"]] = relationship(
        "UserFeed",
        back_populates="feed",
        passive_deletes=True,
    )

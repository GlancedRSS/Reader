"""Article model for unified articles from feeds."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.article_source import ArticleSource
    from backend.models.user_article import UserArticle


class Article(Base):
    """Unified articles from feeds, deduplicated by canonical URL."""

    __tablename__ = "articles"
    __table_args__ = (
        CheckConstraint(
            "public.is_valid_url(canonical_url)",
            name="chk_content_articles_canonical_url",
        ),
        CheckConstraint(
            "length(title) <= 1000",
            name="chk_content_articles_title_length",
        ),
        CheckConstraint(
            "length(author) <= 500",
            name="chk_content_articles_author_length",
        ),
        CheckConstraint(
            "length(summary) <= 2000",
            name="chk_content_articles_summary_length",
        ),
        CheckConstraint(
            "media_url IS NULL OR public.is_valid_url(media_url)",
            name="chk_content_articles_media_url",
        ),
        CheckConstraint(
            "published_at IS NULL OR published_at <= NOW()",
            name="chk_content_articles_published_not_future",
        ),
        Index(
            "idx_content_articles_canonical_url",
            "canonical_url",
        ),
        Index(
            "idx_content_articles_published_id_cursor",
            sa_text("published_at DESC, id DESC"),
        ),
        Index(
            "idx_content_articles_title_trgm",
            sa_text("title"),
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        Index(
            "idx_content_articles_textsearchable",
            sa_text("textsearchable"),
            postgresql_using="gin",
        ),
        Index(
            "idx_content_articles_platform_metadata_gin",
            sa_text("platform_metadata"),
            postgresql_using="gin",
        ),
        {"schema": "content"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        primary_key=True,
        server_default=sa_text("extensions.gen_random_uuid()"),
    )
    canonical_url: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False
    )

    title: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    source_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    media_url: Mapped[str | None] = mapped_column(Text)
    platform_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
        nullable=False,
    )

    # Full-text search vector (stored column, auto-updated by trigger)
    textsearchable: Mapped[Any] = mapped_column(TSVECTOR, nullable=False)

    sources: Mapped[list["ArticleSource"]] = relationship(
        "ArticleSource",
        back_populates="article",
    )
    user_articles: Mapped[list["UserArticle"]] = relationship(
        "UserArticle",
        back_populates="article",
    )

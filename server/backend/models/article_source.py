"""ArticleSource model for article-feed junction table."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.article import Article
    from backend.models.feed import Feed


class ArticleSource(Base):
    """Junction table linking articles to feeds."""

    __tablename__ = "article_sources"
    __table_args__ = (
        UniqueConstraint("article_id", "feed_id"),
        Index("idx_content_article_sources_article_id", "article_id"),
        Index("idx_content_article_sources_feed_id", "feed_id"),
        Index(
            "idx_content_article_sources_article_feed", "article_id", "feed_id"
        ),
        {"schema": "content"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        primary_key=True,
        server_default=sa_text("extensions.gen_random_uuid()"),
    )
    article_id: Mapped[UUID] = mapped_column(
        ForeignKey("content.articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    feed_id: Mapped[UUID] = mapped_column(
        ForeignKey("content.feeds.id", ondelete="CASCADE"),
        nullable=False,
    )

    article: Mapped["Article"] = relationship(
        "Article",
        foreign_keys=[article_id],
        back_populates="sources",
    )
    feed: Mapped["Feed"] = relationship(
        "Feed",
        foreign_keys=[feed_id],
        back_populates="sources",
    )

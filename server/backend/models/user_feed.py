"""UserFeed model for user feed subscriptions."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.feed import Feed
    from backend.models.user_folder import UserFolder


class UserFeed(Base):
    """User subscriptions to feeds."""

    __tablename__ = "user_feeds"
    __table_args__ = (
        CheckConstraint(
            "length(title) <= 200",
            name="chk_content_user_feeds_title_length",
        ),
        CheckConstraint(
            "unread_count >= 0",
            name="chk_content_user_feeds_unread_count",
        ),
        Index(
            "idx_content_user_feeds_pinned_sort",
            sa_text("user_id, is_pinned DESC, created_at DESC"),
        ),
        Index(
            "idx_content_user_feeds_active",
            sa_text("user_id, is_active"),
            postgresql_where=sa_text("is_active = true"),
        ),
        Index(
            "idx_content_user_feeds_folder_id",
            "folder_id",
            postgresql_where=sa_text("folder_id IS NOT NULL"),
        ),
        Index("idx_content_user_feeds_feed_id", "feed_id"),
        Index(
            "idx_content_user_feeds_user_folder",
            "user_id",
            "folder_id",
            postgresql_where=sa_text("folder_id IS NOT NULL"),
        ),
        UniqueConstraint("user_id", "feed_id"),
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
    feed_id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        ForeignKey("content.feeds.id", ondelete="CASCADE"),
        nullable=False,
    )

    folder_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID,
        ForeignKey("personalization.user_folders.id", ondelete="SET NULL"),
    )

    import_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID,
        ForeignKey("management.opml_imports.id", ondelete="SET NULL"),
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    unread_count: Mapped[int] = mapped_column(
        Integer, server_default=sa_text("0")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )

    folder: Mapped["UserFolder | None"] = relationship(
        "UserFolder", overlaps="feeds"
    )
    feed: Mapped["Feed"] = relationship(
        "Feed",
        foreign_keys=[feed_id],
        lazy="selectin",
        back_populates="user_subscriptions",
    )

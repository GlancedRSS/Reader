"""User folder model for feed organization."""

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
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.user_feed import UserFeed


class UserFolder(Base):
    """User-created folders for hierarchical feed organization."""

    __tablename__ = "user_folders"
    __table_args__ = (
        Index("idx_personalization_user_folders_user_id", "user_id"),
        Index("idx_personalization_user_folders_parent_id", "parent_id"),
        Index(
            "idx_personalization_user_folders_pinned_sort",
            sa_text("user_id, is_pinned DESC, name ASC"),
        ),
        Index(
            "idx_personalization_user_folders_user_parent_optimized",
            "user_id",
            "parent_id",
            "depth",
        ),
        UniqueConstraint(
            "user_id", "name", "parent_id", name="unique_user_folder_name"
        ),
        CheckConstraint(
            "depth <= 9", name="chk_personalization_user_folders_depth"
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="chk_personalization_user_folders_name_not_empty",
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
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(16), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID,
        ForeignKey("personalization.user_folders.id", ondelete="SET NULL"),
    )
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    depth: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )

    feeds: Mapped[list["UserFeed"]] = relationship(
        "UserFeed", overlaps="folder"
    )

    parent: Mapped["UserFolder | None"] = relationship(
        "UserFolder",
        remote_side="UserFolder.id",
        back_populates="children",
    )
    children: Mapped[list["UserFolder"]] = relationship(
        "UserFolder",
        back_populates="parent",
        remote_side="UserFolder.parent_id",
    )

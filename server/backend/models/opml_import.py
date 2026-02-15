"""OPML import model for feed subscription imports."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base, PostgresUUID, sa_text


class OpmlImport(Base):
    """OPML import job tracking model."""

    __tablename__ = "opml_imports"
    __table_args__ = (
        CheckConstraint(
            "filename IS NULL OR length(filename) <= 255",
            name="chk_management_opml_imports_filename_length",
        ),
        CheckConstraint(
            "storage_key IS NULL OR length(storage_key) <= 500",
            name="chk_management_opml_imports_storage_key_length",
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'completed_with_errors', 'failed')",
            name="chk_management_opml_imports_status",
        ),
        CheckConstraint(
            "total_feeds >= 0 AND imported_feeds >= 0 AND failed_feeds >= 0 AND duplicate_feeds >= 0",
            name="chk_management_opml_imports_feed_counts",
        ),
        CheckConstraint(
            "imported_feeds + failed_feeds + duplicate_feeds <= total_feeds",
            name="chk_management_opml_imports_stats",
        ),
        Index(
            "idx_management_opml_imports_user_status_created",
            "user_id",
            "status",
            sa_text("created_at DESC"),
            postgresql_where=sa_text(
                "status IN ('pending', 'processing', 'completed_with_errors')"
            ),
        ),
        Index(
            "idx_management_opml_imports_status_created_at",
            "status",
            "created_at",
        ),
        {"schema": "management"},
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

    filename: Mapped[str | None] = mapped_column(Text)
    storage_key: Mapped[str | None] = mapped_column(Text)

    total_feeds: Mapped[int] = mapped_column(Integer, default=0)
    imported_feeds: Mapped[int] = mapped_column(Integer, default=0)
    failed_feeds: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_feeds: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(Text, default="pending")

    failed_feeds_log: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

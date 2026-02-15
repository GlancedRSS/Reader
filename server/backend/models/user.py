"""User model for cookie-based authentication."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, PostgresUUID, sa_text

if TYPE_CHECKING:
    from backend.models.user_tag import UserTag


class User(Base):
    """User account model for authentication and preferences."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "length(username) >= 3 AND length(username) <= 20",
            name="chk_accounts_users_username_length",
        ),
        CheckConstraint(
            "length(password_hash) >= 60",
            name="chk_accounts_users_password_hash_length",
        ),
        CheckConstraint(
            "first_name IS NULL OR length(first_name) <= 32",
            name="chk_accounts_users_first_name_length",
        ),
        CheckConstraint(
            "last_name IS NULL OR length(last_name) <= 32",
            name="chk_accounts_users_last_name_length",
        ),
        Index("idx_accounts_users_username", "username"),
        {"schema": "accounts"},
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        primary_key=True,
        server_default=sa_text("extensions.gen_random_uuid()"),
    )
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
        onupdate=sa_text("NOW()"),
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_active: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        comment="Last time user was active in the app (for engagement tracking)",
    )

    tags: Mapped[list["UserTag"]] = relationship(
        "UserTag", cascade="all, delete-orphan"
    )

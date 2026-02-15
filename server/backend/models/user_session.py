"""User session model for authentication tracking."""

from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base, PostgresUUID, sa_text


class UserSession(Base):
    """User session model for tracking active authentication sessions."""

    __tablename__ = "user_sessions"
    __table_args__ = (
        CheckConstraint(
            "length(cookie_hash) >= 64",
            name="chk_accounts_user_sessions_cookie_hash_length",
        ),
        CheckConstraint(
            "user_agent IS NULL OR length(user_agent) <= 500",
            name="chk_accounts_user_sessions_user_agent_length",
        ),
        Index("idx_accounts_user_sessions_user_id", "user_id"),
        Index("idx_accounts_user_sessions_session_id", "session_id"),
        Index("idx_accounts_user_sessions_expires_at", "expires_at"),
        Index("idx_accounts_user_sessions_cookie_hash", "cookie_hash"),
        Index(
            "idx_accounts_user_sessions_user_id_last_used",
            "user_id",
            sa_text("last_used DESC"),
        ),
        {"schema": "accounts"},
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
    session_id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        server_default=sa_text("extensions.gen_random_uuid()"),
        unique=True,
        nullable=False,
    )

    cookie_hash: Mapped[str] = mapped_column(Text, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )
    last_used: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_text("NOW()")
    )

    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[IPv4Address | IPv6Address | None] = mapped_column(INET)

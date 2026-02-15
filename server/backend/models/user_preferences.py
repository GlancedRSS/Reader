"""User preferences model for application settings."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.domain import UserPreferenceConfig
from backend.models.base import Base, PostgresUUID, sa_text


class UserPreferences(Base):
    """User preferences model for configurable settings."""

    __tablename__ = "user_preferences"
    __table_args__ = (
        *[
            CheckConstraint(
                f"{field_name} IN {tuple(field.choices)}",
                name=f"chk_personalization_user_preferences_{field_name}",
            )
            for field_name, field in UserPreferenceConfig.FIELDS.items()
            if field.choices
        ],
        {"schema": "personalization"},
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID,
        ForeignKey("accounts.users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    theme: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["theme"].default
    )
    show_article_thumbnails: Mapped[bool] = mapped_column(
        Boolean,
        default=UserPreferenceConfig.FIELDS["show_article_thumbnails"].default,
    )
    app_layout: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["app_layout"].default
    )
    article_layout: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["article_layout"].default
    )
    font_spacing: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["font_spacing"].default
    )
    font_size: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["font_size"].default
    )
    feed_sort_order: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["feed_sort_order"].default
    )
    show_feed_favicons: Mapped[bool] = mapped_column(
        Boolean,
        default=UserPreferenceConfig.FIELDS["show_feed_favicons"].default,
    )
    date_format: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["date_format"].default
    )
    time_format: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["time_format"].default
    )
    language: Mapped[str] = mapped_column(
        Text,
        default=UserPreferenceConfig.FIELDS["language"].default,
        nullable=False,
    )
    auto_mark_as_read: Mapped[str] = mapped_column(
        Text, default=UserPreferenceConfig.FIELDS["auto_mark_as_read"].default
    )
    estimated_reading_time: Mapped[bool] = mapped_column(
        Boolean,
        default=UserPreferenceConfig.FIELDS["estimated_reading_time"].default,
    )
    show_summaries: Mapped[bool] = mapped_column(
        Boolean, default=UserPreferenceConfig.FIELDS["show_summaries"].default
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa_text("NOW()"),
    )

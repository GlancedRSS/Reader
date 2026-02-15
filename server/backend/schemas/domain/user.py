"""Schemas for user profile and preferences."""

from datetime import datetime

from pydantic import Field

from backend.schemas.core import BaseSchema


class UserResponse(BaseSchema):
    """GET '/api/v1/me' - Current user profile."""

    username: str = Field(...)
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)
    is_admin: bool = Field(...)
    created_at: datetime = Field(...)
    last_login: datetime | None = Field(None)


class ProfileUpdateRequest(BaseSchema):
    """PUT '/api/v1/me/profile' - Update user profile."""

    first_name: str | None = Field(None, max_length=32)
    last_name: str | None = Field(None, max_length=32)


class PreferencesResponse(BaseSchema):
    """GET '/api/v1/preferences'."""

    theme: str = Field(...)
    show_article_thumbnails: bool = Field(...)
    app_layout: str = Field(...)
    article_layout: str = Field(...)
    font_spacing: str = Field(...)
    font_size: str = Field(...)
    feed_sort_order: str = Field(...)
    show_feed_favicons: bool = Field(...)
    date_format: str = Field(...)
    time_format: str = Field(...)
    language: str = Field(...)
    auto_mark_as_read: str = Field(...)
    estimated_reading_time: bool = Field(...)
    show_summaries: bool = Field(...)


class PreferencesUpdateRequest(BaseSchema):
    """PUT '/api/v1/preferences'."""

    theme: str | None = Field(None)
    show_article_thumbnails: bool | None = Field(None)
    app_layout: str | None = Field(None)
    article_layout: str | None = Field(None)
    font_spacing: str | None = Field(None)
    font_size: str | None = Field(None)
    feed_sort_order: str | None = Field(None)
    show_feed_favicons: bool | None = Field(None)
    date_format: str | None = Field(None)
    time_format: str | None = Field(None)
    language: str | None = Field(None)
    auto_mark_as_read: str | None = Field(None)
    estimated_reading_time: bool | None = Field(None)
    show_summaries: bool | None = Field(None)

"""Schemas for authentication endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class RegistrationRequest(BaseSchema):
    """Request schema for user registration."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Unique username (letters, numbers, underscores, hyphens)",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, must contain letter and number)",
    )


class LoginRequest(BaseSchema):
    """Request schema for user login."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="User password")


class PasswordChangeRequest(BaseSchema):
    """Request schema for changing password."""

    current_password: str = Field(
        ..., description="Current password for verification"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (min 8 chars, must contain letter and number)",
    )


class SessionResponse(BaseSchema):
    """Response schema for a user session."""

    session_id: UUID = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="When session was created")
    last_used: datetime = Field(..., description="When session was last used")
    expires_at: datetime = Field(..., description="When session expires")
    user_agent: str | None = Field(None, description="User agent string")
    ip_address: str | None = Field(None, description="IP address")
    current: bool = Field(
        ..., description="Whether this is the current session"
    )

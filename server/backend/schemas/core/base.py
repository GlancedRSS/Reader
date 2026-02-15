"""Base schemas, mixins, and common utilities used across the application."""

from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        """Pydantic configuration for base schemas."""

        from_attributes = True
        extra = "ignore"


class TimestampedSchema(BaseSchema):
    """Base schema with timestamp fields."""

    created_at: datetime

"""Schemas for background job management."""

from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class JobCreateResponse(BaseSchema):
    """Response for job creation in background operations."""

    job_id: UUID = Field(...)
    message: str = Field(...)

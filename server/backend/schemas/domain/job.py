from uuid import UUID

from pydantic import Field

from backend.schemas.core import BaseSchema


class JobCreateResponse(BaseSchema):
    job_id: UUID = Field(...)
    message: str = Field(...)

from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        extra = "ignore"


class TimestampedSchema(BaseSchema):
    created_at: datetime

"""SQLAlchemy base configuration and common types."""

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

PostgresUUID = UUID
sa_text = text

"""Shared base SQLModel classes and generic models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from app.core.security import get_datetime_utc


class UUIDModel(SQLModel):
    """Base model providing a UUID primary key."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class TimestampModel(SQLModel):
    """Base model providing a timezone-aware created_at timestamp."""

    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class Message(SQLModel):
    """Generic message response schema."""

    message: str


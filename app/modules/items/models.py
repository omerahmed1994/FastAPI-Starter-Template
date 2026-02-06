import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.common.models import TimestampModel, UUIDModel

if TYPE_CHECKING:
    from app.modules.users.models import User


class Item(UUIDModel, TimestampModel, table=True):  # type: ignore[misc]
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional["User"] = Relationship(back_populates="items")


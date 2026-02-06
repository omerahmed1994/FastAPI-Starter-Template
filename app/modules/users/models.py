from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.common.models import TimestampModel, UUIDModel

if TYPE_CHECKING:
    from app.modules.items.models import Item


class User(UUIDModel, TimestampModel, table=True):  # type: ignore[misc]
    email: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)
    hashed_password: str
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)


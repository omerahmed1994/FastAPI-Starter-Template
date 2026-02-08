"""Item-related business logic and database interactions."""

import uuid
from typing import List, Tuple

from sqlmodel import Session, select

from app.common.service import BaseService, paginate
from app.modules.items.dtos import ItemCreate, ItemUpdate
from app.modules.items.models import Item


class ItemService(BaseService[Item, ItemCreate, ItemUpdate]):
    """Item service for handling business logic for items."""

    def get_by_owner(
        self,
        session: Session,
        *,
        owner_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Item], int]:
        """Fetch paginated items belonging to a specific owner."""
        statement = (
            select(self.model)
            .where(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        # Use common pagination if complex, or simple multi here
        return self.get_multi_by_owner(session, owner_id=owner_id, skip=skip, limit=limit)

    def get_multi_by_owner(
        self, session: Session, *, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Item], int]:
        """Custom fetch for owner-specific items with counts."""
        statement = select(self.model).where(self.model.owner_id == owner_id)
        return paginate(session, statement, skip=skip, limit=limit)


# Export an instance of ItemService
item_service = ItemService(Item)

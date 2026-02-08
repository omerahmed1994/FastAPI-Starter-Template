"""Item endpoints router, delegating to items.service."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.common.models import Message
from app.common.dtos import Paginated
from app.modules.items.service import item_service
from app.modules.items.dtos import ItemCreate, ItemPublic, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=Paginated[ItemPublic])
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """Fetch items for the current user."""
    if current_user.is_superuser:
        items, count = item_service.get_multi(session=session, skip=skip, limit=limit)
    else:
        items, count = item_service.get_multi_by_owner(
            session=session, owner_id=current_user.id, skip=skip, limit=limit
        )
    return Paginated(data=items, count=count, skip=skip, limit=limit)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Fetch a single item."""
    item = item_service.get(session=session, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """Create a new item."""
    return item_service.create(
        session=session, obj_in=item_in, owner_id=current_user.id
    )


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """Update an item."""
    db_item = item_service.get(session=session, id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (db_item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item_service.update(session=session, db_obj=db_item, obj_in=item_in)


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """Delete an item."""
    db_item = item_service.get(session=session, id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (db_item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    item_service.delete(session=session, id=id)
    return Message(message="Item deleted successfully")


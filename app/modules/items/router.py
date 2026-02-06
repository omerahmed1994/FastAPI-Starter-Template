"""Item endpoints router, delegating to items.service."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.common.models import Message
from app.common.schemas import Paginated
from app.modules.items import service
from app.modules.items.schemas import ItemCreate, ItemPublic, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=Paginated[ItemPublic])
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    items, count = service.get_items_for_user(
        session=session,
        owner_id=current_user.id,
        is_superuser=current_user.is_superuser,
        skip=skip,
        limit=limit,
    )
    return Paginated(data=items, count=count, skip=skip, limit=limit)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    item = service.get_item(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    return service.create_item(
        session=session, owner_id=current_user.id, item_in=item_in
    )


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    db_item = service.get_item(session=session, item_id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (db_item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return service.update_item(session=session, db_item=db_item, item_in=item_in)


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    db_item = service.get_item(session=session, item_id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (db_item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    service.delete_item(session=session, db_item=db_item)
    return Message(message="Item deleted successfully")


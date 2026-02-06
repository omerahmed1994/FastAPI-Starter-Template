"""Item-related business logic and database interactions."""

import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.modules.items.models import Item
from app.modules.items.schemas import ItemCreate, ItemUpdate


def get_items_for_user(
    *, session: Session, owner_id: uuid.UUID | None, is_superuser: bool, skip: int, limit: int
) -> tuple[list[Item], int]:
    if is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = (
            select(Item).order_by(Item.created_at.desc()).offset(skip).limit(limit)
        )
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == owner_id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .order_by(Item.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()
    return items, count


def get_item(*, session: Session, item_id: uuid.UUID) -> Item | None:
    return session.get(Item, item_id)


def create_item(
    *, session: Session, owner_id: uuid.UUID, item_in: ItemCreate
) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def update_item(
    *, session: Session, db_item: Item, item_in: ItemUpdate
) -> Item:
    update_dict = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_dict)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(*, session: Session, db_item: Item) -> None:
    session.delete(db_item)
    session.commit()


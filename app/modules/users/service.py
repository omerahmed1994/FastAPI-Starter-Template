"""User-related business logic and database interactions."""

from typing import Any
import uuid

from fastapi import HTTPException
from sqlmodel import Session, col, delete, func, select

from app.core.security import get_password_hash, verify_password
from app.modules.items.models import Item
from app.modules.users.models import User
from app.modules.users.dtos import (
    UpdatePassword,
    UserCreate,
    UserUpdate,
    UserUpdateMe,
)

# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw"
    "$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate_user(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def change_password(
    *, session: Session, db_user: User, body: UpdatePassword
) -> None:
    verified, _ = verify_password(body.current_password, db_user.hashed_password)
    if not verified:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as the current one",
        )
    hashed_password = get_password_hash(body.new_password)
    db_user.hashed_password = hashed_password
    session.add(db_user)
    session.commit()


def update_current_user(
    *, session: Session, current_user: User, user_in: UserUpdateMe
) -> User:
    """Update fields of the currently authenticated user."""
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


from app.common.service import paginate

def list_users(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[User], int]:
    """Return users ordered by creation date and total count."""
    statement = select(User).order_by(User.created_at.desc())
    return paginate(session, statement, skip=skip, limit=limit)


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def delete_current_user(*, session: Session, current_user: User) -> None:
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Super users are not allowed to delete themselves",
        )
    session.delete(current_user)
    session.commit()


def delete_user(
    *, session: Session, current_user: User, user_id: uuid.UUID
) -> None:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403,
            detail="Super users are not allowed to delete themselves",
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()


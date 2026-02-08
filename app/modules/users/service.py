"""User-related business logic and database interactions."""

import uuid
from typing import Any, Optional

from fastapi import HTTPException
from sqlmodel import Session, col, delete, select

from app.common.service import BaseService, paginate
from app.core.security import get_password_hash, verify_password
from app.modules.items.models import Item
from app.modules.users.dtos import (
    UpdatePassword,
    UserCreate,
    UserUpdate,
    UserUpdateMe,
)
from app.modules.users.models import User

# Dummy hash for timing attack prevention
DUMMY_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw"
    "$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
)


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """User service for handling business logic for users."""

    def create_user(self, session: Session, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        db_obj = self.model.model_validate(
            obj_in, update={"hashed_password": get_password_hash(obj_in.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update_user(self, session: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """Update user data, including password hashing if provided."""
        user_data = obj_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        
        db_obj.sqlmodel_update(user_data, update=extra_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_by_email(self, session: Session, *, email: str) -> Optional[User]:
        """Fetch a user by email."""
        statement = select(self.model).where(self.model.email == email)
        return session.exec(statement).first()

    def authenticate(self, session: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        db_user = self.get_by_email(session, email=email)
        if not db_user:
            verify_password(password, DUMMY_HASH)
            return None
        
        verified, updated_hash = verify_password(password, db_user.hashed_password)
        if not verified:
            return None
        
        if updated_hash:
            db_user.hashed_password = updated_hash
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
        return db_user

    def change_password(self, session: Session, *, db_user: User, body: UpdatePassword) -> None:
        """Change a user's password with verification."""
        verified, _ = verify_password(body.current_password, db_user.hashed_password)
        if not verified:
            raise HTTPException(status_code=400, detail="Incorrect password")
        
        if body.current_password == body.new_password:
            raise HTTPException(
                status_code=400,
                detail="New password cannot be the same as the current one",
            )
        
        db_user.hashed_password = get_password_hash(body.new_password)
        session.add(db_user)
        session.commit()

    def delete_with_items(self, session: Session, *, current_user: User, user_id: uuid.UUID) -> None:
        """Delete a user and all their associated items."""
        user = self.get(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user == current_user and current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="Super users are not allowed to delete themselves",
            )
        
        # Delete items first (or rely on CASCADE if configured correctly in DB)
        statement = delete(Item).where(col(Item.owner_id) == user_id)
        session.exec(statement)  # type: ignore
        session.delete(user)
        session.commit()


# Export an instance of UserService
user_service = UserService(User)

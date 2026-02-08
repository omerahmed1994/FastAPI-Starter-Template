"""Database engine and initialization helpers."""

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.modules.users.models import User
from app.modules.users.dtos import UserCreate
from app.modules.users.service import create_user

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    """Initialize the database with the first superuser if needed."""
    # Tables should be created with Alembic migrations.
    # If you don't want to use migrations, you could create the tables here:
    # from sqlmodel import SQLModel
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        create_user(session=session, user_create=user_in)


import uuid
from typing import Any, Generic, List, Tuple, Type, TypeVar, Optional, Union

from pydantic import BaseModel
from sqlmodel import Session, func, select, SQLModel
from sqlmodel.sql.expression import Select, SelectOfScalar

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateDto = TypeVar("CreateDto", bound=BaseModel)
UpdateDto = TypeVar("UpdateDto", bound=BaseModel)


class BaseService(Generic[ModelType, CreateDto, UpdateDto]):
    def __init__(self, model: Type[ModelType]):
        """
        Base class for services that handle CRUD operations.
        
        Args:
            model: The SQLModel model class.
        """
        self.model = model

    def get(self, session: Session, id: uuid.UUID) -> Optional[ModelType]:
        """Fetch a single record by ID."""
        return session.get(self.model, id)

    def get_multi(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ModelType], int]:
        """Fetch multiple records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        count_statement = select(func.count()).select_from(self.model)
        
        data = session.exec(statement).all()
        count = session.exec(count_statement).one()
        
        return list(data), count

    def create(self, session: Session, *, obj_in: CreateDto, **kwargs: Any) -> ModelType:
        """
        Create a new record.
        
        Args:
            session: Database session.
            obj_in: DTO containing data for creation.
            **kwargs: Additional fields to set on the model (e.g., owner_id).
        """
        db_obj = self.model.model_validate(obj_in, update=kwargs)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateDto, dict[str, Any]],
    ) -> ModelType:
        """Update an existing record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, *, id: uuid.UUID) -> Optional[ModelType]:
        """Delete a record by ID."""
        db_obj = session.get(self.model, id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
        return db_obj


T = TypeVar("T")


def paginate(
    session: Session,
    statement: SelectOfScalar[T] | Select[T],
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[Any], int]:
    """
    Standardized pagination helper for custom queries.
    """
    # Get total count using a subquery
    count_statement = select(func.count()).select_from(statement.subquery())
    count = session.exec(count_statement).one()

    # Get paginated data
    paginated_statement = statement.offset(skip).limit(limit)
    data = session.exec(paginated_statement).all()

    return list(data), count

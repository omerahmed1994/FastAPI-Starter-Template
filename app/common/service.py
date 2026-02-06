from typing import Any, List, Tuple, Type, TypeVar
from sqlmodel import Session, func, select
from sqlmodel.sql.expression import Select, SelectOfScalar

T = TypeVar("T")

def paginate(
    session: Session,
    statement: SelectOfScalar[T] | Select[T],
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[T], int]:
    """
    Standardized pagination helper.
    Executes a count query and a slice query.
    """
    # Get total count using a subquery to handle filters correctly
    count_statement = select(func.count()).select_from(statement.subquery())
    count = session.exec(count_statement).one()

    # Get paginated data
    paginated_statement = statement.offset(skip).limit(limit)
    data = session.exec(paginated_statement).all()

    return list(data), count

from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Paginated(BaseModel, Generic[T]):
    """
    Generic schema for paginated responses.
    """
    data: List[T]
    count: int
    limit: int
    skip: int

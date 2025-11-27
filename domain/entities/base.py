from abc import ABC
from typing import Any
from pydantic import BaseModel, validator

class ValueObject(BaseModel):
    """Базовый класс для Value Objects"""
    
    class Config:
        frozen = True
        allow_mutation = False
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ValueObject):
            return False
        return self.dict() == other.dict()

class AggregateRoot(ABC):
    """Базовый класс для Aggregate Roots"""
    pass

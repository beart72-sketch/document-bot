from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum
from .base import ValueObject

class Currency(Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"

@dataclass(frozen=True)
class Money:
    """Value Object для денежных сумм"""
    amount: float
    currency: Currency = Currency.RUB
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        return Money(self.amount * factor, self.currency)

@dataclass(frozen=True)
class Address:
    """Value Object для адреса"""
    street: str
    city: str
    postal_code: str
    country: str = "Russia"
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.postal_code}, {self.country}"

class PersonalInfo(ValueObject):
    """Персональная информация"""
    full_name: str
    phone: str
    email: str

    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip().split()) < 2:
            raise ValueError('Full name must contain first and last name')
        return v

class DocumentContent(ValueObject):
    """Содержимое документа"""
    template: str
    filled_fields: Dict[str, str]
    final_content: Optional[str] = None

    @validator('template')
    def validate_template(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Template must be at least 10 characters long')
        return v

class TemplateMetadata(ValueObject):
    """Метаданные шаблона"""
    complexity: str
    time_estimate: str
    legal_importance: str
    is_premium: bool = False
    category: str

    @validator('complexity')
    def validate_complexity(cls, v):
        allowed_levels = ['low', 'medium', 'high', 'expert']
        if v not in allowed_levels:
            raise ValueError(f'Complexity must be one of {allowed_levels}')
        return v

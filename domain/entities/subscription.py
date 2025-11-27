from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

@dataclass
class Subscription:
    """Доменная модель подписки"""
    id: str
    user_id: str
    subscription_type: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_valid(self) -> bool:
        """Проверяет действительна ли подписка"""
        return self.is_active and datetime.utcnow() <= self.end_date
    
    def days_remaining(self) -> int:
        """Возвращает количество оставшихся дней подписки"""
        if not self.is_active:
            return 0
        remaining = self.end_date - datetime.utcnow()
        return max(0, remaining.days)

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
from uuid import uuid4

class SubscriptionPlan(Enum):
    """Планы подписок"""
    FREE = "free"
    PREMIUM = "premium"
    BUSINESS = "business"

class SubscriptionStatus(Enum):
    """Статусы подписки"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

@dataclass
class Subscription:
    """Доменная модель подписки"""
    id: str
    user_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    start_date: datetime
    end_date: datetime
    features: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Проверяет активна ли подписка"""
        return (self.status == SubscriptionStatus.ACTIVE and 
                datetime.utcnow() <= self.end_date)
    
    def days_remaining(self) -> int:
        """Оставшиеся дни подписки"""
        if not self.is_active():
            return 0
        return (self.end_date - datetime.utcnow()).days
    
    def upgrade(self, new_plan: SubscriptionPlan, duration_days: int = 30):
        """Обновление подписки"""
        self.plan = new_plan
        self.status = SubscriptionStatus.ACTIVE
        self.start_date = datetime.utcnow()
        self.end_date = self.start_date + timedelta(days=duration_days)
        self.updated_at = datetime.utcnow()
    
    def cancel(self):
        """Отмена подписки"""
        self.status = SubscriptionStatus.CANCELLED
        self.updated_at = datetime.utcnow()

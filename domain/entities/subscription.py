from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

class SubscriptionPlan(Enum):
    FREE = "free"
    PREMIUM = "premium"
    BUSINESS = "business"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class Subscription:
    id: str
    user_id: str
    plan: str
    status: str
    start_date: datetime
    end_date: datetime
    features: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        return (
            self.status == SubscriptionStatus.ACTIVE.value and
            self.end_date >= datetime.utcnow()
        )

    def days_remaining(self) -> int:
        days = (self.end_date - datetime.utcnow()).days
        return max(0, days)

    def upgrade(self, new_plan: str, duration_days: int = 30):
        self.plan = new_plan
        self.end_date = datetime.utcnow() + timedelta(days=duration_days)
        self.status = SubscriptionStatus.ACTIVE.value
        self.updated_at = datetime.utcnow()

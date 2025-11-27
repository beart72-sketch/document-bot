from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from domain.entities.user import User

class UserResponse(BaseModel):
    id: str
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    role: str
    subscription_type: str
    is_subscription_active: bool
    last_activity: datetime
    created_at: datetime
    
    @classmethod
    def from_domain(cls, user: User) -> 'UserResponse':
        return cls(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            role=user.role,
            subscription_type=user.subscription_type,
            is_subscription_active=user.is_subscription_active,
            last_activity=user.last_activity,
            created_at=user.created_at
        )

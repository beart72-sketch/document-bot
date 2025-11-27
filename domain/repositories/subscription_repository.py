from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.subscription import Subscription, SubscriptionPlan, SubscriptionStatus

class SubscriptionRepository(ABC):
    """Порт для репозитория подписок"""
    
    @abstractmethod
    async def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    async def get_active_subscriptions(self) -> List[Subscription]:
        pass
    
    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription:
        pass
    
    @abstractmethod
    async def update(self, subscription: Subscription) -> Subscription:
        pass
    
    @abstractmethod
    async def delete(self, subscription_id: str) -> bool:
        pass

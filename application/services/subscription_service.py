from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from domain.entities.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from domain.entities.user import User
from domain.repositories.subscription_repository import SubscriptionRepository
from domain.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self, subscription_repo: SubscriptionRepository, user_repo: UserRepository):
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        
        self.plan_limits = {
            "free": {
                "documents_per_month": 5,
                "templates_access": ["basic"],
                "ai_requests": 10,
                "max_document_length": 1000
            },
            "premium": {
                "documents_per_month": 50,
                "templates_access": ["basic", "premium"],
                "ai_requests": 100,
                "max_document_length": 5000
            },
            "business": {
                "documents_per_month": 500,
                "templates_access": ["basic", "premium", "business"],
                "ai_requests": 1000,
                "max_document_length": 20000
            }
        }
    
    async def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        try:
            return await self.subscription_repo.get_by_user_id(user_id)
        except Exception as e:
            logger.error(f"❌ Ошибка в get_user_subscription: {e}")
            return None
    
    async def create_free_subscription(self, user_id: str) -> Subscription:
        try:
            existing_subscription = await self.get_user_subscription(user_id)
            if existing_subscription:
                return existing_subscription
            
            subscription = Subscription(
                id=str(uuid4()),
                user_id=user_id,
                plan=SubscriptionPlan.FREE.value,
                status=SubscriptionStatus.ACTIVE.value,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365 * 10),
                features=self.plan_limits["free"]
            )
            
            return await self.subscription_repo.create(subscription)
        except Exception as e:
            logger.error(f"❌ Ошибка в create_free_subscription: {e}")
            return Subscription(
                id=str(uuid4()),
                user_id=user_id,
                plan=SubscriptionPlan.FREE.value,
                status=SubscriptionStatus.ACTIVE.value,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365 * 10),
                features=self.plan_limits["free"]
            )
    
    async def get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription or not self._is_active(subscription):
                subscription = await self.create_free_subscription(user_id)
            
            return {
                "plan": subscription.plan,
                "status": subscription.status,
                "is_active": self._is_active(subscription),
                "days_remaining": self._days_remaining(subscription),
                "features": subscription.features,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date
            }
        except Exception as e:
            logger.error(f"❌ Ошибка в get_subscription_info: {e}")
            return {
                "plan": "free",
                "status": "active",
                "is_active": True,
                "days_remaining": 3650,
                "features": self.plan_limits["free"],
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=365 * 10)
            }
    
    async def check_document_limit(self, user_id: str, current_month_documents: int) -> bool:
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription or not self._is_active(subscription):
                subscription = await self.create_free_subscription(user_id)
            
            limit = subscription.features.get("documents_per_month", 5)
            return current_month_documents < limit
        except Exception as e:
            logger.error(f"❌ Ошибка в check_document_limit: {e}")
            return current_month_documents < 5
    
    async def get_remaining_documents(self, user_id: str, current_month_documents: int) -> int:
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription or not self._is_active(subscription):
                subscription = await self.create_free_subscription(user_id)
            
            limit = subscription.features.get("documents_per_month", 5)
            return max(0, limit - current_month_documents)
        except Exception as e:
            logger.error(f"❌ Ошибка в get_remaining_documents: {e}")
            return max(0, 5 - current_month_documents)
    
    async def can_use_ai(self, user_id: str, used_ai_requests: int) -> bool:
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription or not self._is_active(subscription):
                subscription = await self.create_free_subscription(user_id)
            
            limit = subscription.features.get("ai_requests", 10)
            return used_ai_requests < limit
        except Exception as e:
            logger.error(f"❌ Ошибка в can_use_ai: {e}")
            return used_ai_requests < 10
    
    async def upgrade_subscription(self, user_id: str, new_plan: str, duration_days: int = 30) -> Subscription:
        try:
            subscription = await self.get_user_subscription(user_id)
            
            if not subscription:
                subscription = Subscription(
                    id=str(uuid4()),
                    user_id=user_id,
                    plan=new_plan,
                    status=SubscriptionStatus.ACTIVE.value,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=duration_days),
                    features=self.plan_limits.get(new_plan, self.plan_limits["free"])
                )
                return await self.subscription_repo.create(subscription)
            
            subscription.plan = new_plan
            subscription.status = SubscriptionStatus.ACTIVE.value
            subscription.end_date = datetime.utcnow() + timedelta(days=duration_days)
            subscription.features = self.plan_limits.get(new_plan, self.plan_limits["free"])
            subscription.updated_at = datetime.utcnow()
            
            return await self.subscription_repo.update(subscription)
        except Exception as e:
            logger.error(f"❌ Ошибка в upgrade_subscription: {e}")
            raise
    
    def _is_active(self, subscription: Subscription) -> bool:
        return (
            subscription.status == SubscriptionStatus.ACTIVE.value and
            subscription.end_date >= datetime.utcnow()
        )
    
    def _days_remaining(self, subscription: Subscription) -> int:
        days = (subscription.end_date - datetime.utcnow()).days
        return max(0, days)

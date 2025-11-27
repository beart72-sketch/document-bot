from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
from domain.entities.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from domain.entities.user import User
from domain.repositories.subscription_repository import SubscriptionRepository
from domain.repositories.user_repository import UserRepository

class SubscriptionService:
    """Сервис для управления подписками"""
    
    def __init__(self, subscription_repo: SubscriptionRepository, user_repo: UserRepository):
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        
        # Лимиты для каждого плана
        self.plan_limits = {
            SubscriptionPlan.FREE: {
                "documents_per_month": 5,
                "templates_access": ["basic"],
                "ai_requests": 10,
                "max_document_length": 1000
            },
            SubscriptionPlan.PREMIUM: {
                "documents_per_month": 50,
                "templates_access": ["basic", "premium"],
                "ai_requests": 100,
                "max_document_length": 5000
            },
            SubscriptionPlan.BUSINESS: {
                "documents_per_month": 500,
                "templates_access": ["basic", "premium", "business"],
                "ai_requests": 1000,
                "max_document_length": 20000
            }
        }
    
    async def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Получает подписку пользователя"""
        return await self.subscription_repo.get_by_user_id(user_id)
    
    async def create_free_subscription(self, user_id: str) -> Subscription:
        """Создает бесплатную подписку для нового пользователя"""
        # Проверяем, нет ли уже подписки
        existing_subscription = await self.get_user_subscription(user_id)
        if existing_subscription:
            return existing_subscription
        
        # Создаем бесплатную подписку
        subscription = Subscription(
            id=str(uuid4()),
            user_id=user_id,
            plan=SubscriptionPlan.FREE,
            status=SubscriptionStatus.ACTIVE,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365 * 10),  # 10 лет
            features=self.plan_limits[SubscriptionPlan.FREE]
        )
        
        return await self.subscription_repo.create(subscription)
    
    async def upgrade_subscription(self, user_id: str, new_plan: SubscriptionPlan, duration_days: int = 30) -> Subscription:
        """Обновляет подписку пользователя"""
        subscription = await self.get_user_subscription(user_id)
        
        if not subscription:
            # Создаем новую подписку если нет существующей
            subscription = Subscription(
                id=str(uuid4()),
                user_id=user_id,
                plan=new_plan,
                status=SubscriptionStatus.ACTIVE,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=duration_days),
                features=self.plan_limits[new_plan]
            )
            return await self.subscription_repo.create(subscription)
        
        # Обновляем существующую подписку
        subscription.upgrade(new_plan, duration_days)
        subscription.features = self.plan_limits[new_plan]
        
        return await self.subscription_repo.update(subscription)
    
    async def check_document_limit(self, user_id: str, current_month_documents: int) -> bool:
        """Проверяет не превышен ли лимит документов"""
        subscription = await self.get_user_subscription(user_id)
        if not subscription or not subscription.is_active():
            subscription = await self.create_free_subscription(user_id)
        
        limit = subscription.features.get("documents_per_month", 5)
        return current_month_documents < limit
    
    async def get_remaining_documents(self, user_id: str, current_month_documents: int) -> int:
        """Возвращает оставшееся количество документов в месяце"""
        subscription = await self.get_user_subscription(user_id)
        if not subscription or not subscription.is_active():
            subscription = await self.create_free_subscription(user_id)
        
        limit = subscription.features.get("documents_per_month", 5)
        return max(0, limit - current_month_documents)
    
    async def can_use_ai(self, user_id: str, used_ai_requests: int) -> bool:
        """Проверяет может ли пользователь использовать AI"""
        subscription = await self.get_user_subscription(user_id)
        if not subscription or not subscription.is_active():
            subscription = await self.create_free_subscription(user_id)
        
        limit = subscription.features.get("ai_requests", 10)
        return used_ai_requests < limit
    
    async def get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """Возвращает информацию о подписке пользователя"""
        subscription = await self.get_user_subscription(user_id)
        if not subscription or not subscription.is_active():
            subscription = await self.create_free_subscription(user_id)
        
        return {
            "plan": subscription.plan.value,
            "status": subscription.status.value,
            "is_active": subscription.is_active(),
            "days_remaining": subscription.days_remaining(),
            "features": subscription.features,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date
        }

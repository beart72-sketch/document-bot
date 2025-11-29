from typing import Optional, List
import logging
from domain.models.subscription import Subscription
from domain.repositories.subscription_repository import SubscriptionRepository
from infrastructure.database.models import SubscriptionModel
from sqlalchemy import select

logger = logging.getLogger(__name__)

class SubscriptionRepositoryImpl(SubscriptionRepository):
    def __init__(self, database):
        self.database = database
    
    async def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        try:
            async with self.database.async_session() as session:
                result = await session.get(SubscriptionModel, subscription_id)
                if result:
                    return self._to_entity(result)
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения подписки по ID {subscription_id}: {e}")
            return None
    
    async def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        try:
            async with self.database.async_session() as session:
                stmt = select(SubscriptionModel).where(SubscriptionModel.user_id == user_id)
                result = await session.execute(stmt)
                subscription_model = result.scalar_one_or_none()
                
                if subscription_model:
                    return self._to_entity(subscription_model)
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения подписки по user_id {user_id}: {e}")
            return None
    
    async def get_all(self) -> List[Subscription]:
        async with self.database.async_session() as session:
            stmt = select(SubscriptionModel)
            result = await session.execute(stmt)
            subscriptions = result.scalars().all()
            return [self._to_entity(sub) for sub in subscriptions]
    
    async def create(self, subscription: Subscription) -> Subscription:
        async with self.database.async_session() as session:
            subscription_model = SubscriptionModel(
                id=subscription.id,
                user_id=subscription.user_id,
                plan=subscription.plan,
                status=subscription.status,
                start_date=subscription.start_date,
                end_date=subscription.end_date,
                features=subscription.features,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            )
            session.add(subscription_model)
            await session.commit()
            return subscription
    
    async def update(self, subscription: Subscription) -> Subscription:
        async with self.database.async_session() as session:
            subscription_model = await session.get(SubscriptionModel, subscription.id)
            if subscription_model:
                subscription_model.plan = subscription.plan
                subscription_model.status = subscription.status
                subscription_model.start_date = subscription.start_date
                subscription_model.end_date = subscription.end_date
                subscription_model.features = subscription.features
                subscription_model.updated_at = subscription.updated_at
                await session.commit()
            return subscription
    
    async def delete(self, subscription_id: str) -> bool:
        async with self.database.async_session() as session:
            subscription_model = await session.get(SubscriptionModel, subscription_id)
            if subscription_model:
                await session.delete(subscription_model)
                await session.commit()
                return True
            return False
    
    def _to_entity(self, model: SubscriptionModel) -> Subscription:
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            plan=model.plan,
            status=model.status,
            start_date=model.start_date,
            end_date=model.end_date,
            features=model.features,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

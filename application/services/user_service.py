from typing import Optional
from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from application.services.subscription_service import SubscriptionService
from uuid import uuid4
from datetime import datetime

class UserService:
    def __init__(self, user_repo: UserRepository, subscription_service: SubscriptionService):
        self.user_repo = user_repo
        self.subscription_service = subscription_service

    async def get_or_create_user(self, telegram_id: int, username: str = None,
                               first_name: str = "", last_name: str = None) -> User:
        """Получает существующего пользователя или создает нового"""
        # Ищем пользователя
        user = await self.user_repo.get_by_telegram_id(telegram_id)

        if user:
            return user

        # Создаем нового пользователя
        new_user = User(
            id=str(uuid4()),
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=None,
            role="user",
            subscription_type="free",
            subscription_start=None,
            subscription_end=None,
            is_subscription_active=False,
            settings={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        user = await self.user_repo.create(new_user)

        # Создаем бесплатную подписку для нового пользователя
        await self.subscription_service.create_free_subscription(user.id)

        return user

    async def update_user_activity(self, user_id: int) -> None:
        """Обновляет активность пользователя"""
        user = await self.user_repo.get_by_telegram_id(user_id)
        if user:
            await self.user_repo.update_activity(user.id)

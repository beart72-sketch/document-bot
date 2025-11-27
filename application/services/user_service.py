from typing import Optional
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from uuid import uuid4
from datetime import datetime

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
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
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.user_repo.create(new_user)
    
    async def update_user_activity(self, telegram_id: int) -> None:
        """Обновляет активность пользователя"""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user:
            # Обновляем время активности через репозиторий
            await self.user_repo.update_activity(user.id)

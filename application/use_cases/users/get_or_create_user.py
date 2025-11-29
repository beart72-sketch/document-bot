from typing import Optional
from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from application.dtos.user_dtos import UserResponse

class GetOrCreateUserUseCase:
    """Use Case для получения или создания пользователя"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def execute(self, telegram_id: int, username: Optional[str] = None, 
                     first_name: Optional[str] = None, last_name: Optional[str] = None) -> UserResponse:
        # Ищем существующего пользователя
        existing_user = await self._user_repository.get_by_telegram_id(telegram_id)
        
        if existing_user:
            # Обновляем активность существующего пользователя
            await self._user_repository.update_activity(telegram_id)
            return UserResponse.from_domain(existing_user)
        
        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        created_user = await self._user_repository.create(user)
        return UserResponse.from_domain(created_user)

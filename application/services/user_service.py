from typing import Optional
from domain.repositories.user_repository import UserRepository
from application.use_cases.users.get_or_create_user import GetOrCreateUserUseCase
from application.dtos.user_dtos import UserResponse

class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
        self._get_or_create_user_use_case = GetOrCreateUserUseCase(user_repository)
    
    async def get_or_create_user(self, telegram_id: int, username: Optional[str] = None, 
                               first_name: Optional[str] = None, last_name: Optional[str] = None) -> UserResponse:
        """Получает или создает пользователя"""
        return await self._get_or_create_user_use_case.execute(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
    
    async def update_user_activity(self, telegram_id: int) -> None:
        """Обновляет активность пользователя"""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if user:
            await self._user_repository.update_activity(telegram_id)

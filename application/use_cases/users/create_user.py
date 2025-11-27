from typing import Optional
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from application.dtos.user_dtos import CreateUserRequest, UserResponse

class CreateUserUseCase:
    """Use Case для создания пользователя"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def execute(self, request: CreateUserRequest) -> UserResponse:
        # Проверяем, существует ли пользователь
        existing_user = await self._user_repository.get_by_telegram_id(request.telegram_id)
        if existing_user:
            return UserResponse.from_domain(existing_user)
        
        # Создаем нового пользователя
        user = User(
            telegram_id=request.telegram_id,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email
        )
        
        created_user = await self._user_repository.create(user)
        return UserResponse.from_domain(created_user)

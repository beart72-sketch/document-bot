from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.user import User

class UserRepository(ABC):
    """Порт для репозитория пользователей"""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def update_activity(self, telegram_id: int) -> None:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[User]:
        pass

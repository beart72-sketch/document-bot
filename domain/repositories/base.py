from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

T = TypeVar("T")

class AsyncRepository(Generic[T], ABC):
    """Абстрактный асинхронный репозиторий"""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass

class SQLAlchemyRepository(AsyncRepository[T], ABC):
    """Базовая реализация репозитория на SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    @property
    @abstractmethod
    def model_class(self):
        pass
    
    async def get_by_id(self, id: str) -> Optional[T]:
        result = await self._session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[T]:
        result = await self._session.execute(select(self.model_class))
        return result.scalars().all()
    
    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def update(self, entity: T) -> T:
        await self._session.merge(entity)
        await self._session.flush()
        return entity
    
    async def delete(self, id: str) -> bool:
        result = await self._session.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )
        return result.rowcount > 0

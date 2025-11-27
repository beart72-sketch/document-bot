from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from domain.repositories.user_repository import UserRepository
from domain.entities.user import User
from infrastructure.database.models import UserModel
from datetime import datetime

class UserRepositoryImpl(UserRepository):
    """Реализация репозитория пользователей на SQLAlchemy 2.0+"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()
        return self._to_domain(db_user) if db_user else None
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        db_user = result.scalar_one_or_none()
        return self._to_domain(db_user) if db_user else None
    
    async def create(self, user: User) -> User:
        db_user = UserModel(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            role=user.role,
            subscription_type=user.subscription_type,
            subscription_start=user.subscription_start,
            subscription_end=user.subscription_end,
            is_subscription_active=user.is_subscription_active,
            settings=user.settings,
            last_activity=user.last_activity
        )
        self._session.add(db_user)
        await self._session.commit()
        await self._session.refresh(db_user)
        return self._to_domain(db_user)
    
    async def update(self, user: User) -> User:
        db_user = await self._session.get(UserModel, user.id)
        if db_user:
            for key, value in user.__dict__.items():
                if key != 'id' and hasattr(db_user, key):
                    setattr(db_user, key, value)
            await self._session.commit()
            return self._to_domain(db_user)
        return None
    
    async def update_activity(self, telegram_id: int) -> None:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.telegram_id == telegram_id)
            .values(last_activity=datetime.utcnow())
        )
        await self._session.commit()
    
    async def get_all(self) -> List[User]:
        result = await self._session.execute(select(UserModel))
        return [self._to_domain(db_user) for db_user in result.scalars().all()]
    
    def _to_domain(self, db_user: UserModel) -> User:
        """Преобразует модель БД в доменную модель"""
        return User(
            id=db_user.id,
            telegram_id=db_user.telegram_id,
            username=db_user.username,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            email=db_user.email,
            role=db_user.role,
            subscription_type=db_user.subscription_type,
            subscription_start=db_user.subscription_start,
            subscription_end=db_user.subscription_end,
            is_subscription_active=db_user.is_subscription_active,
            settings=db_user.settings,
            last_activity=db_user.last_activity,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )

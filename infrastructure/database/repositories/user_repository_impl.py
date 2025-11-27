from typing import Optional, List
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel
from sqlalchemy import select, update

class UserRepositoryImpl(UserRepository):
    def __init__(self, database):
        self.database = database
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        async with self.database.async_session() as session:
            result = await session.get(UserModel, user_id)
            if result:
                return self._to_entity(result)
            return None
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        async with self.database.async_session() as session:
            stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user_model = result.scalar_one_or_none()
            if user_model:
                return self._to_entity(user_model)
            return None
    
    async def get_all(self) -> List[User]:
        async with self.database.async_session() as session:
            stmt = select(UserModel)
            result = await session.execute(stmt)
            users = result.scalars().all()
            return [self._to_entity(user) for user in users]
    
    async def create(self, user: User) -> User:
        async with self.database.async_session() as session:
            user_model = UserModel(
                id=user.id,
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
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            session.add(user_model)
            await session.commit()
            return user
    
    async def update(self, user: User) -> User:
        async with self.database.async_session() as session:
            user_model = await session.get(UserModel, user.id)
            if user_model:
                user_model.username = user.username
                user_model.first_name = user.first_name
                user_model.last_name = user.last_name
                user_model.email = user.email
                user_model.role = user.role
                user_model.subscription_type = user.subscription_type
                user_model.subscription_start = user.subscription_start
                user_model.subscription_end = user.subscription_end
                user_model.is_subscription_active = user.is_subscription_active
                user_model.settings = user.settings
                user_model.updated_at = user.updated_at
                await session.commit()
            return user
    
    async def update_activity(self, user_id: str) -> None:
        """Обновляет время активности пользователя"""
        async with self.database.async_session() as session:
            from datetime import datetime
            stmt = update(UserModel).where(
                UserModel.id == user_id
            ).values(updated_at=datetime.utcnow())
            await session.execute(stmt)
            await session.commit()
    
    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            telegram_id=model.telegram_id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            role=model.role,
            subscription_type=model.subscription_type,
            subscription_start=model.subscription_start,
            subscription_end=model.subscription_end,
            is_subscription_active=model.is_subscription_active,
            settings=model.settings,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

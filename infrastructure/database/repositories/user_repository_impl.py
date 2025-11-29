from typing import Optional, List
import logging
from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel
from sqlalchemy import select

logger = logging.getLogger(__name__)

class UserRepositoryImpl(UserRepository):
    def __init__(self, database):
        self.database = database
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        try:
            async with self.database.async_session() as session:
                result = await session.get(UserModel, user_id)
                if result:
                    return self._to_entity(result)
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя по ID {user_id}: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            async with self.database.async_session() as session:
                stmt = select(UserModel).where(UserModel.email == email)
                result = await session.execute(stmt)
                user_model = result.scalar_one_or_none()
                
                if user_model:
                    return self._to_entity(user_model)
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя по email {email}: {e}")
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
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                profile_data=user.profile_data,
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
                user_model.email = user.email
                user_model.first_name = user.first_name
                user_model.last_name = user.last_name
                user_model.is_active = user.is_active
                user_model.profile_data = user.profile_data
                user_model.updated_at = user.updated_at
                await session.commit()
            return user
    
    async def delete(self, user_id: str) -> bool:
        async with self.database.async_session() as session:
            user_model = await session.get(UserModel, user_id)
            if user_model:
                await session.delete(user_model)
                await session.commit()
                return True
            return False
    
    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            is_active=model.is_active,
            profile_data=model.profile_data,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

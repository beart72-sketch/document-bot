from infrastructure.database.database import Database
from infrastructure.database.models import UserModel
from datetime import datetime
import uuid
import asyncio

async def register_user():
    db = Database()
    await db.initialize()
    
    async with db.async_session() as session:
        # Проверяем, есть ли уже пользователь
        from sqlalchemy import select
        stmt = select(UserModel).where(UserModel.telegram_id == 7743484813)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"✅ Пользователь уже существует: {existing_user.first_name}")
        else:
            # Создаем нового пользователя
            new_user = UserModel(
                id=str(uuid.uuid4()),
                telegram_id=7743484813,
                username="BaluBars",
                first_name="balu",
                role="user",
                subscription_type="free",
                is_subscription_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_user)
            await session.commit()
            print(f"✅ Пользователь создан: {new_user.first_name} (ID: {new_user.telegram_id})")

if __name__ == "__main__":
    asyncio.run(register_user())

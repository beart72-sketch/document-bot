#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы
"""
import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_system():
    try:
        print("🧪 Тестирование системы...")
        
        # 1. Проверяем конфигурацию
        from core.config import load_config
        config = load_config()
        print(f"✅ Конфигурация: {config.database.url}")
        
        # 2. Проверяем базу данных
        from infrastructure.database.database import database
        await database.create_tables()
        health = await database.health_check()
        print(f"✅ База данных: {health}")
        
        # 3. Проверяем модели домена
        from domain.models.user import User
        from domain.models.value_objects import PersonalInfo
        
        user = User(
            telegram_id=123456789,
            personal_info=PersonalInfo(first_name="Test", last_name="User")
        )
        print(f"✅ Модели домена: создан пользователь {user.full_name}")
        
        # 4. Проверяем репозитории
        from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
        
        async for session in database.get_session():
            user_repo = UserRepositoryImpl(session)
            
            # Сохраняем пользователя
            saved_user = await user_repo.save(user)
            print(f"✅ Репозиторий: пользователь сохранен с ID {saved_user.id}")
            
            # Ищем пользователя
            found_user = await user_repo.get_by_telegram_id(123456789)
            print(f"✅ Репозиторий: пользователь найден - {found_user.full_name}")
            break
        
        print("🎉 Все тесты пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_system())

#!/usr/bin/env python3
"""Скрипт для пересоздания таблиц базы данных с новой структурой"""
import asyncio
from infrastructure.database.database import Database

async def recreate_tables():
    print("🔄 Пересоздаем таблицы базы данных с новой структурой...")
    
    database = Database()
    
    # Удаляем существующие таблицы
    await database.drop_tables()
    print("✅ Старые таблицы удалены")
    
    # Создаем новые таблицы
    await database.create_tables()
    print("✅ Новые таблицы созданы")
    
    # Проверяем структуру
    if await database.health_check():
        print("✅ База данных работает корректно")
    else:
        print("❌ Ошибка базы данных")

if __name__ == "__main__":
    asyncio.run(recreate_tables())

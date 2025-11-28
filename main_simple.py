#!/usr/bin/env python3
"""
Упрощенная версия запуска бота для тестирования
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import config


async def main():
    """Основная функция запуска бота"""
    
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Запуск упрощенной версии бота")
    
    try:
        # Инициализируем бот и диспетчер
        bot = Bot(token=config.get_bot_token())
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Базовые обработчики
        @dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            await message.answer("🤖 Бот запущен! Команда /start работает!")
        
        @dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            await message.answer("📖 Это помощь по боту!")
        
        @dp.message(F.text)
        async def echo(message: types.Message):
            if not message.text.startswith('/'):
                await message.answer(f"🔁 Эхо: {message.text}")
        
        logger.info("✅ Бот инициализирован")
        logger.info("🔄 Запуск обработки сообщений...")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Простейшая версия бота для быстрого запуска
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Простая конфигурация
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]


async def main():
    """Основная функция запуска бота"""
    
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    if not TOKEN:
        logger.error("❌ Токен бота не установлен!")
        return
    
    logger.info("🚀 Запуск простого Document Bot")
    
    try:
        # Инициализируем бот и диспетчер
        bot = Bot(token=TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Базовые обработчики
        @dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            await message.answer(
                "🤖 Добро пожаловать в Document Bot!\n\n"
                "Доступные команды:\n"
                "/start - Начать работу\n"
                "/help - Помощь\n"
                "/metrics - Метрики (только для админов)\n\n"
                "Напиши любое сообщение для эха!"
            )
        
        @dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            await message.answer(
                "📖 Document Bot - бот для работы с документами.\n\n"
                "Функции:\n"
                "• Обработка документов\n"
                "• Управление файлами\n"
                "• Поиск по содержимому"
            )
        
        @dp.message(Command("metrics"))
        async def cmd_metrics(message: types.Message):
            if message.from_user.id in ADMIN_IDS:
                await message.answer(
                    "📊 Метрики бота:\n"
                    "• Статус: 🟢 Работает\n"
                    "• Пользователей: 1\n"
                    "• Сообщений: 10+"
                )
            else:
                await message.answer("❌ Эта команда только для администраторов")
        
        @dp.message(F.text)
        async def echo(message: types.Message):
            if not message.text.startswith('/'):
                await message.answer(f"🔁 Вы написали: {message.text}")
        
        logger.info("✅ Бот инициализирован")
        logger.info(f"👤 Администраторы: {ADMIN_IDS}")
        logger.info("🔄 Запуск обработки сообщений...")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")

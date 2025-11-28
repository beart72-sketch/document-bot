#!/usr/bin/env python3
"""
Главный файл запуска бота с улучшенной обработкой ошибок, кэшированием и мониторингом
Для aiogram 3.x
"""

import asyncio
import logging
from pathlib import Path

# Наша улучшенная конфигурация
from config import config, print_config_summary

# Импорты aiogram 3.x
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импорты наших модулей
from handlers import register_handlers
from error_handlers import error_handler
from cache import initialize_caching, shutdown_caching
from metrics import initialize_monitoring, shutdown_monitoring


def setup_logging():
    """Настраивает систему логирования"""
    log_level = getattr(logging, config.logging.LOG_LEVEL)
    
    # Базовая конфигурация
    logging.basicConfig(
        level=log_level,
        format=config.logging.LOG_FORMAT,
        handlers=[]
    )
    
    logger = logging.getLogger()
    
    # Хендлер для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(config.logging.LOG_FORMAT))
    logger.addHandler(console_handler)
    
    # Хендлер для файла (если включено)
    if config.logging.ENABLE_FILE_LOGGING:
        # Создаём директорию для логов если нужно
        log_file = Path(config.logging.LOGS_DIR) / "bot.log"
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(config.logging.LOG_FORMAT))
        logger.addHandler(file_handler)
    
    return logger


async def main():
    """Основная функция запуска бота"""
    
    # Выводим информацию о конфигурации
    if config.DEBUG:
        print_config_summary()
    
    # Настраиваем логирование
    logger = setup_logging()
    logger.info("🚀 Запуск Document Bot со всеми системами")
    logger.info(f"🔧 Режим отладки: {'ВКЛ' if config.DEBUG else 'ВЫКЛ'}")
    logger.info(f"📊 Уровень логирования: {config.logging.LOG_LEVEL}")
    
    try:
        # Инициализируем систему кэширования
        await initialize_caching()
        logger.info("✅ Система кэширования инициализирована")
        
        # Инициализируем систему мониторинга
        await initialize_monitoring()
        logger.info("✅ Система мониторинга инициализирована")
        
        # Инициализируем бот и диспетчер
        bot = Bot(token=config.get_bot_token())
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Регистрируем обработчики
        await register_handlers(dp)
        
        logger.info("✅ Бот инициализирован успешно")
        logger.info(f"👤 Администраторы: {config.get_admin_ids()}")
        
        # Запускаем поллинг
        logger.info("🔄 Запуск обработки сообщений...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
        error_handler.log_error_with_context(e, level="CRITICAL")
        raise
    
    finally:
        # Всегда останавливаем системы при выходе
        await shutdown_monitoring()
        await shutdown_caching()
        logger.info("🛑 Остановка бота")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")

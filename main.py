"""Main application entry point."""
import asyncio
import signal
import sys

from infrastructure.bootstrap import create_app
from infrastructure.config import load_config
from infrastructure.logging import setup_logging

async def main():
    """Основная функция приложения"""
    # Загрузка конфигурации
    config = load_config()
    
    # Настройка логирования ДО создания app чтобы видеть логи инициализации
    log_config = config.get('logging', {})
    setup_logging(
        log_level=log_config.get('level', 'INFO'),
        log_to_file=log_config.get('file_enabled', True)
    )
    
    # Импортируем логгер после настройки логирования
    import logging
    logger = logging.getLogger(__name__)
    
    # Создание приложения
    app = await create_app(config)
    
    # Обработка сигналов для graceful shutdown
    def signal_handler(signum, frame):
        print(f"Получен сигнал {signum}, завершаем работу...")
        asyncio.create_task(shutdown(app))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("🚀 Starting bot...")
        # Запуск бота
        await app.dispatcher.start_polling(
            app.bot, 
            allowed_updates=app.dispatcher.resolve_used_update_types(),
            handle_signals=False  # Мы сами обрабатываем сигналы
        )
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        await shutdown(app)

async def shutdown(app):
    """Корректное завершение работы"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🔻 Завершение работы приложения...")
    await app.cleanup()
    logger.info("✅ Приложение корректно завершено")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())

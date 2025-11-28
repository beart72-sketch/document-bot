"""Пакет обработчиков для бота
Для aiogram 3.x"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

async def register_handlers(dp: Dispatcher):
    """Регистрирует все обработчики в диспетчере"""
    logger.info("🔄 Начинаем регистрацию обработчиков...")
    
    # 1. Сначала регистрируем базовые команды (/start, /help)
    from .base_handlers import register_base_handlers
    await register_base_handlers(dp)
    logger.info("✅ Базовые обработчики зарегистрированы")
    
    # 2. Затем регистрируем метрики (/metrics, /health, /performance)
    from .metrics_handlers import register_metrics_handlers
    await register_metrics_handlers(dp)
    logger.info("✅ Обработчики метрик зарегистрированы")
    
    # 3. Регистрируем обработчики кнопок меню
    from .button_handlers import register_button_handlers
    await register_button_handlers(dp)
    logger.info("✅ Обработчики кнопок зарегистрированы")
    
    # 4. В САМОМ КОНЦЕ регистрируем fallback-обработчик
    from .unknown_handlers import register_unknown_handlers
    await register_unknown_handlers(dp)
    logger.info("✅ Fallback-обработчики зарегистрированы")
    
    logger.info("🎯 Все обработчики успешно зарегистрированы")

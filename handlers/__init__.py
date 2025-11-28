"""Регистрация всех обработчиков в правильном порядке"""

import logging
from aiogram import Dispatcher

from .base_handlers import register_base_handlers
from .document_handlers import register_document_handlers  # ← ДО кнопок!
from .button_handlers import register_button_handlers
from .metrics_handlers import register_metrics_handlers
from .unknown_handlers import register_unknown_handlers

logger = logging.getLogger(__name__)

async def register_handlers(dp: Dispatcher):
    logger.info("🔄 Начинаем регистрацию обработчиков...")
    
    await register_base_handlers(dp)
    await register_document_handlers(dp)  # ← FSM должен быть выше кнопок!
    await register_button_handlers(dp)
    await register_metrics_handlers(dp)
    await register_unknown_handlers(dp)  # ← fallback — всегда последним
    
    logger.info("🎯 Все обработчики успешно зарегистрированы")

"""Регистрация всех обработчиков"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

# Импортируем все роутеры
from .main_handlers import main_router
from .document_creation_handlers import document_creation_router

async def register_handlers(dp: Dispatcher):
    """Асинхронная регистрация всех роутеров"""
    # Важен порядок: FSM обработчики должны быть первыми
    dp.include_router(document_creation_router)
    dp.include_router(main_router)
    
    logger.info("✅ Все обработчики зарегистрированы")

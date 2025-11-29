"""Регистрация всех обработчиков"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

from .main_handlers import main_router

async def register_handlers(dp: Dispatcher):
    """Асинхронная регистрация всех роутеров"""
    dp.include_router(main_router)
    logger.info("✅ Все обработчики зарегистрированы")

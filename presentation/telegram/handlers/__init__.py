"""Регистрация всех обработчиков"""

import logging
from aiogram import Dispatcher

logger = logging.getLogger(__name__)

# Импортируем main_router (теперь он точно есть)
from presentation.telegram.handlers.main_handlers import main_router

async def register_handlers(dp: Dispatcher):
    dp.include_router(main_router)
    logger.info("✅ Все обработчики зарегистрированы")

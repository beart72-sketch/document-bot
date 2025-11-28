"""
Базовые обработчики команд для бота
Для aiogram 3.x
"""

import logging
from aiogram import Dispatcher, Router, types, F
from aiogram.filters import Command

from metrics import BotMetrics, performance_monitor

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    logger.info(f"🟢 Обработчик /start вызван пользователем {message.from_user.id}")
    await message.answer(
        "🤖 Добро пожаловать в Document Bot!\n\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
        "/metrics - Метрики бота (только для админов)\n"
        "/health - Статус здоровья (только для админов)\n"
        "/performance - Отчет производительности (только для админов)"
    )


@router.message(Command("help"))
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    logger.info(f"🟢 Обработчик /help вызван пользователем {message.from_user.id}")
    await message.answer(
        "📖 Помощь по Document Bot:\n\n"
        "Этот бот предназначен для работы с документами.\n\n"
        "Основные функции:\n"
        "• Загрузка документов\n"
        "• Управление документами\n"
        "• Поиск по документам\n\n"
        "Используйте команды из меню для навигации."
    )


async def register_base_handlers(dp: Dispatcher):
    """Регистрирует базовые обработчики"""
    dp.include_router(router)
    logger.info("🟢 Базовые обработчики: /start, /help")

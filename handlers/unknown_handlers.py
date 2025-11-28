"""
Обработчики для неизвестных команд и сообщений
"""

import logging
from aiogram import Dispatcher, Router, types, F
from aiogram.filters import Command

from metrics import BotMetrics, performance_monitor

router = Router()
logger = logging.getLogger(__name__)

# Список известных команд
KNOWN_COMMANDS = {"start", "help", "metrics", "health", "performance", "reset_metrics"}


@router.message(F.text.startswith("/"))
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def unknown_command(message: types.Message):
    """Обработчик неизвестных команд"""
    # Получаем команду (убираем / и берём первое слово)
    command_text = message.text[1:].split()[0].lower()
    
    logger.info(f"🔴 Неизвестная команда: /{command_text} от пользователя {message.from_user.id}")
    
    # Если команда не в списке известных
    if command_text not in KNOWN_COMMANDS:
        await message.answer(
            f"❌ Неизвестная команда: /{command_text}\n\n"
            "Используйте /help для списка доступных команд."
        )


@router.message(F.text)
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def unknown_text(message: types.Message):
    """Обработчик неизвестных текстовых сообщений (включая кнопки)"""
    logger.info(f"🔴 Неизвестный текст: '{message.text}' от пользователя {message.from_user.id}")
    await message.answer(
        "❌ Не понимаю эту команду.\n\n"
        "Используйте /help для списка доступных команд."
    )


async def register_unknown_handlers(dp: Dispatcher):
    """Регистрирует обработчики неизвестных команд"""
    dp.include_router(router)
    logger.info("🔴 Fallback-обработчики зарегистрированы (должны быть последними!)")

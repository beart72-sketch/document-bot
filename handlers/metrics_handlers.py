"""
Обработчики для работы с метриками и мониторингом
Для aiogram 3.x
"""

import logging
from aiogram import Dispatcher, Router, types
from aiogram.filters import Command

from metrics_api import metrics_api
from metrics import BotMetrics, performance_monitor

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("metrics"))
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def cmd_metrics(message: types.Message):
    """Обработчик команды /metrics"""
    logger.info(f"🟢 Обработчик /metrics вызван пользователем {message.from_user.id}")
    response = await metrics_api.get_metrics_summary(message)
    await message.answer(response, parse_mode="Markdown")


@router.message(Command("health"))
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def cmd_health(message: types.Message):
    """Обработчик команды /health"""
    logger.info(f"🟢 Обработчик /health вызван пользователем {message.from_user.id}")
    response = await metrics_api.get_health_status(message)
    await message.answer(response, parse_mode="Markdown")


@router.message(Command("performance"))
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def cmd_performance(message: types.Message):
    """Обработчик команды /performance"""
    logger.info(f"🟢 Обработчик /performance вызван пользователем {message.from_user.id}")
    response = await metrics_api.get_performance_report(message)
    await message.answer(response, parse_mode="Markdown")


@router.message(Command("reset_metrics"))
@BotMetrics.track_message()
@performance_monitor.track_telegram_handler()
async def cmd_reset_metrics(message: types.Message):
    """Обработчик команды /reset_metrics"""
    logger.info(f"🟢 Обработчик /reset_metrics вызван пользователем {message.from_user.id}")
    response = await metrics_api.reset_metrics(message)
    await message.answer(response)


async def register_metrics_handlers(dp: Dispatcher):
    """Регистрирует обработчики метрик"""
    dp.include_router(router)
    logger.info("🟢 Обработчики метрик: /metrics, /health, /performance, /reset_metrics")

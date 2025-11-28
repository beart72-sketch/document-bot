"""Инициализация приложения — адаптировано под ваш .env"""

import logging
import os
from typing import NamedTuple

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from handlers import register_handlers
from error_handlers import error_handler

class AppContext(NamedTuple):
    bot: Bot
    dp: Dispatcher
    config: Config

logger = logging.getLogger(__name__)

async def initialize_app() -> AppContext:
    logger.info("🔧 Начало инициализации приложения...")
    
    config = Config()
    debug_mode = getattr(config, 'DEBUG', os.getenv("DEBUG", "false").lower() == "true")
    if debug_mode:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🟢 Режим отладки: ВКЛ")
    
    # 🔑 Ищем токен в порядке приоритета (ваш .env использует TELEGRAM_BOT_TOKEN)
    token = None
    for attr in ["TELEGRAM_BOT_TOKEN", "BOT_TOKEN", "TELEGRAM_TOKEN"]:
        if hasattr(config, attr):
            token = getattr(config, attr)
        if not token:
            token = os.getenv(attr)
        if token:
            break
    
    if not token:
        raise ValueError("❌ Токен бота не найден. Проверьте TELEGRAM_BOT_TOKEN в .env")
    
    admin_ids = _parse_admin_ids(config)
    if not admin_ids:
        logger.warning("⚠️ ADMIN_IDS не заданы")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    await register_handlers(dp)
    logger.info("✅ Обработчики зарегистрированы")
    
    @dp.shutdown()
    async def on_shutdown():
        logger.info("♻️ Graceful shutdown...")
        await bot.session.close()
        logger.info("✅ Ресурсы освобождены")
    
    logger.info("✅ Инициализация завершена")
    return AppContext(bot=bot, dp=dp, config=config)

def _parse_admin_ids(config):
    for attr in ["ADMIN_IDS", "ADMINS"]:
        if hasattr(config, attr):
            ids = getattr(config, attr)
            if isinstance(ids, str):
                return [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
            elif isinstance(ids, (list, tuple)):
                return [int(x) for x in ids if str(x).isdigit()]
            elif isinstance(ids, int):
                return [ids]
    env_ids = os.getenv("ADMIN_IDS", "")
    return [int(x) for x in env_ids.split(",") if x.strip().isdigit()]

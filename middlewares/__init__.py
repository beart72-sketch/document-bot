"""
Middleware пакет для бота
Для aiogram 3.x
"""

from aiogram import Dispatcher, Bot

from .error_middleware import setup_error_handling


async def register_middlewares(dp: Dispatcher, bot: Bot):
    """Регистрирует все middleware в диспетчере"""
    setup_error_handling(dp, bot)
    # Здесь можно добавить другие middleware

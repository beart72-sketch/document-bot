"""
Middleware для автоматической обработки ошибок в хендлерах
Для aiogram 3.x
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from error_handlers import error_handler

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    """Middleware для перехвата и обработки ошибок"""
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """Обрабатывает события"""
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Ошибка в обработчике: {e}")
            
            # Пробуем обработать ошибку
            message = data.get('message')
            callback_query = data.get('callback_query')
            
            await error_handler.handle_telegram_error(e, message, callback_query)
            return None


def setup_error_handling(dp, bot):
    """
    Настраивает обработку ошибок для диспетчера
    """
    # Регистрируем middleware
    dp.update.middleware(ErrorMiddleware())
    
    # Регистрируем глобальные обработчики ошибок
    @dp.errors()
    async def global_error_handler(event, exception: Exception):
        """Глобальный обработчик ошибок"""
        try:
            update = event.update
            message = update.message if update.message else None
            callback = update.callback_query if update.callback_query else None
            
            handled = await error_handler.handle_telegram_error(exception, message, callback)
            if handled:
                return True
                
            # Логируем необработанные ошибки
            error_handler.log_error_with_context(
                exception,
                {
                    "update_id": update.update_id,
                    "user_id": update.message.from_user.id if update.message else 
                              update.callback_query.from_user.id if update.callback_query else None
                },
                level="ERROR"
            )
        
        except Exception as e:
            logger.critical(f"Критическая ошибка в глобальном обработчике: {e}")
        
        return False

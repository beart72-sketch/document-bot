"""Error handling middleware for Aiogram."""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update, TelegramObject

from .telegram_errors import TelegramErrorHandler

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseMiddleware):
    """Middleware for global error handling in Aiogram."""
    
    def __init__(self):
        self.error_handler = TelegramErrorHandler()
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"❌ Unhandled error in middleware: {e}")
            
            # Try to handle the error
            message_or_callback = None
            if hasattr(event, 'message') and event.message:
                message_or_callback = event.message
            elif hasattr(event, 'callback_query') and event.callback_query:
                message_or_callback = event.callback_query
            
            await self.error_handler.handle_telegram_error(e, message_or_callback)
            
            # Don't re-raise to prevent bot from crashing
            return None

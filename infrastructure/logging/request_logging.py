"""Request logging middleware for Aiogram."""
import time
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseMiddleware):
    """Middleware for logging incoming requests."""
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        
        # Log incoming request
        await self._log_incoming_request(event)
        
        try:
            result = await handler(event, data)
            execution_time = time.time() - start_time
            
            # Log successful processing
            await self._log_successful_processing(event, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log processing error
            await self._log_processing_error(event, e, execution_time)
            
            raise
    
    async def _log_incoming_request(self, event: Update):
        """Log incoming request details."""
        try:
            if event.message:
                await self._log_message(event.message)
            elif event.callback_query:
                await self._log_callback(event.callback_query)
            elif event.edited_message:
                logger.info(f"✏️ Edited message from {event.edited_message.from_user.id}")
            else:
                logger.debug(f"📨 Unknown update type: {event.update_id}")
        except Exception as e:
            logger.error(f"❌ Error logging incoming request: {e}")
    
    async def _log_message(self, message: Message):
        """Log incoming message."""
        user = message.from_user
        log_data = {
            'user_id': user.id,
            'username': user.username,
            'message_type': 'text',
            'content': message.text or '[media]'
        }
        
        logger.info(
            f"📨 Message from {user.id} (@{user.username}): "
            f"{message.text or '[media]'}"
        )
    
    async def _log_callback(self, callback: CallbackQuery):
        """Log incoming callback."""
        user = callback.from_user
        logger.info(
            f"🖱️ Callback from {user.id} (@{user.username}): "
            f"{callback.data}"
        )
    
    async def _log_successful_processing(self, event: Update, execution_time: float):
        """Log successful request processing."""
        user_id = self._extract_user_id(event)
        
        logger.debug(
            f"✅ Request processed for user {user_id} "
            f"in {execution_time:.3f}s"
        )
        
        # Log slow processing
        if execution_time > 1.0:
            logger.warning(
                f"🐢 Slow request processing for user {user_id}: "
                f"{execution_time:.3f}s"
            )
    
    async def _log_processing_error(self, event: Update, error: Exception, execution_time: float):
        """Log request processing error."""
        user_id = self._extract_user_id(event)
        
        logger.error(
            f"❌ Request processing failed for user {user_id} "
            f"after {execution_time:.3f}s: {error}"
        )
    
    def _extract_user_id(self, event: Update) -> str:
        """Extract user ID from update."""
        if event.message:
            return str(event.message.from_user.id)
        elif event.callback_query:
            return str(event.callback_query.from_user.id)
        elif event.edited_message:
            return str(event.edited_message.from_user.id)
        else:
            return "unknown"

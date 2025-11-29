"""Telegram-specific error handling."""
import logging
from typing import Optional, Union
from aiogram import types
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError

from .error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class TelegramErrorHandler(ErrorHandler):
    """Error handler for Telegram-specific errors."""
    
    def __init__(self):
        super().__init__()
        # Add Telegram-specific error mappings
        self.known_errors.update({
            'message_not_modified': '✅',  # Silent handling for this case
            'message_to_edit_not_found': '⚠️ Сообщение устарело. Используйте актуальные кнопки.',
            'message_to_delete_not_found': '✅',  # Silent handling
            'chat_not_found': '⚠️ Чат не найден. Перезапустите бота командой /start.',
            'user_is_bot': '⚠️ Эта функция недоступна для ботов.'
        })
    
    async def handle_telegram_error(
        self, 
        error: Exception, 
        message_or_callback: Optional[Union[types.Message, types.CallbackQuery]] = None
    ) -> bool:
        """Handle Telegram-specific errors."""
        try:
            if isinstance(error, TelegramBadRequest):
                return await self._handle_telegram_bad_request(error, message_or_callback)
            elif isinstance(error, TelegramNetworkError):
                return await self._handle_network_error(error, message_or_callback)
            else:
                return await self._handle_generic_error(error, message_or_callback)
        except Exception as e:
            logger.error(f"❌ Error in error handler: {e}")
            return False
    
    async def _handle_telegram_bad_request(
        self, 
        error: TelegramBadRequest, 
        message_or_callback: Optional[Union[types.Message, types.CallbackQuery]] = None
    ) -> bool:
        """Handle TelegramBadRequest exceptions."""
        error_message = str(error).lower()
        
        # Handle specific Telegram errors silently
        if 'message is not modified' in error_message:
            logger.debug("ℹ️ Message not modified - ignoring")
            return True
        elif 'message to edit not found' in error_message:
            logger.warning("⚠️ Message to edit not found")
            if message_or_callback:
                await self._send_error_message(message_or_callback, 'message_to_edit_not_found')
            return True
        elif 'message to delete not found' in error_message:
            logger.debug("ℹ️ Message to delete not found - ignoring")
            return True
        elif 'chat not found' in error_message:
            logger.error("❌ Chat not found")
            if message_or_callback:
                await self._send_error_message(message_or_callback, 'chat_not_found')
            return True
        
        # Log unhandled Telegram errors
        logger.error(f"❌ Unhandled TelegramBadRequest: {error}")
        if message_or_callback:
            await self._send_error_message(message_or_callback, 'unknown_error')
        return False
    
    async def _handle_network_error(
        self, 
        error: TelegramNetworkError, 
        message_or_callback: Optional[Union[types.Message, types.CallbackQuery]] = None
    ) -> bool:
        """Handle network-related errors."""
        logger.warning(f"🌐 Network error: {error}")
        if message_or_callback:
            await self._send_error_message(message_or_callback, 'network_error')
        return True
    
    async def _handle_generic_error(
        self, 
        error: Exception, 
        message_or_callback: Optional[Union[types.Message, types.CallbackQuery]] = None
    ) -> bool:
        """Handle generic errors."""
        logger.error(f"❌ Generic error: {error}")
        self.log_error(error)
        
        if message_or_callback:
            user_message = self.get_user_message(error)
            if user_message != self.known_errors['unknown_error']:  # Don't send generic unknown errors
                await self._send_error_message(message_or_callback, user_message)
        
        return False
    
    async def _send_error_message(
        self, 
        message_or_callback: Union[types.Message, types.CallbackQuery], 
        error_key: str
    ):
        """Send error message to user."""
        try:
            if isinstance(message_or_callback, types.CallbackQuery):
                # For callbacks, try to edit message or send new one
                try:
                    error_msg = self.known_errors.get(error_key, self.known_errors['unknown_error'])
                    if error_msg != '✅':  # Don't send silent errors
                        await message_or_callback.message.answer(error_msg)
                    await message_or_callback.answer()  # Always answer callback
                except Exception as e:
                    logger.error(f"❌ Failed to send error to callback: {e}")
            elif isinstance(message_or_callback, types.Message):
                # For messages, send new message
                error_msg = self.known_errors.get(error_key, self.known_errors['unknown_error'])
                if error_msg != '✅':  # Don't send silent errors
                    await message_or_callback.answer(error_msg)
        except Exception as e:
            logger.error(f"❌ Failed to send error message: {e}")

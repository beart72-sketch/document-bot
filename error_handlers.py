"""
Модуль для обработки ошибок и исключений в боте.
Обеспечивает централизованную обработку всех типов ошибок.
Для aiogram 3.x
"""

import logging
import traceback
from typing import Optional, Dict, Any

# Импорты aiogram 3.x
from aiogram import types
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)

from core.config import config

# Настраиваем логгер для ошибок
logger = logging.getLogger(__name__)


class ErrorHandler:
    """Класс для обработки различных типов ошибок"""
    
    # Словарь с пользовательскими сообщениями для разных типов ошибок
    ERROR_MESSAGES = {
        "default": "❌ Произошла непредвиденная ошибка. Попробуйте позже.",
        "network": "🌐 Проблемы с соединением. Проверьте интернет и попробуйте снова.",
        "file_too_large": "📁 Файл слишком большой. Максимальный размер: {max_size} MB",
        "invalid_file_format": "📄 Неподдерживаемый формат файла. Разрешены: {allowed_formats}",
        "permission_denied": "🔐 У вас нет прав для выполнения этой операции.",
        "message_not_found": "📝 Сообщение не найдено. Возможно, оно было удалено.",
        "rate_limit": "⏰ Слишком много запросов. Подождите {cooldown} секунд.",
        "database_error": "🗄️ Ошибка базы данных. Попробуйте позже.",
        "validation_error": "📋 Ошибка в данных: {details}",
    }
    
    @classmethod
    async def handle_telegram_error(
        cls, 
        error: Exception, 
        message: types.Message = None,
        callback: types.CallbackQuery = None
    ) -> bool:
        """
        Обрабатывает ошибки Telegram API
        Возвращает True если ошибка обработана, False если нужно пробросить дальше
        """
        user_message = None
        
        try:
            if isinstance(error, TelegramRetryAfter):
                # Ограничение частоты запросов
                retry_after = getattr(error, 'retry_after', 30)
                user_message = cls.ERROR_MESSAGES["rate_limit"].format(cooldown=retry_after)
                logger.warning(f"Rate limit: {error}, retry after: {retry_after}")
                
            elif isinstance(error, TelegramBadRequest):
                error_str = str(error).lower()
                if "message to delete not found" in error_str:
                    logger.warning(f"Сообщение для удаления не найдено: {error}")
                    return True
                elif "not enough rights" in error_str or "forbidden" in error_str:
                    user_message = cls.ERROR_MESSAGES["permission_denied"]
                elif "message not found" in error_str:
                    user_message = cls.ERROR_MESSAGES["message_not_found"]
                else:
                    user_message = cls.ERROR_MESSAGES["default"]
                logger.error(f"BadRequest ошибка: {error}")
                
            elif isinstance(error, TelegramForbiddenError):
                user_message = cls.ERROR_MESSAGES["permission_denied"]
                logger.warning(f"Доступ запрещен: {error}")
                
            elif isinstance(error, TelegramNetworkError):
                user_message = cls.ERROR_MESSAGES["network"]
                logger.error(f"Сетевая ошибка: {error}")
                
            elif isinstance(error, TelegramAPIError):
                user_message = cls.ERROR_MESSAGES["default"]
                logger.error(f"Telegram API ошибка: {error}")
                
            else:
                # Общая обработка для любых ошибок
                error_str = str(error).lower()
                if "not found" in error_str:
                    user_message = cls.ERROR_MESSAGES["message_not_found"]
                elif "forbidden" in error_str or "permission" in error_str:
                    user_message = cls.ERROR_MESSAGES["permission_denied"]
                elif "network" in error_str or "connection" in error_str:
                    user_message = cls.ERROR_MESSAGES["network"]
                else:
                    user_message = cls.ERROR_MESSAGES["default"]
                logger.error(f"Необработанная ошибка: {error}")
                
            # Отправляем сообщение пользователю
            if user_message and (message or callback):
                await cls._send_error_message(user_message, message, callback)
                
            return True
            
        except Exception as e:
            logger.critical(f"Критическая ошибка в обработчике ошибок: {e}")
            return False
    
    @classmethod
    async def handle_file_error(
        cls,
        error: Exception,
        message: types.Message,
        file_type: str = "файл"
    ) -> None:
        """Обрабатывает ошибки связанные с файлами"""
        user_message = None
        
        if "file too large" in str(error).lower():
            max_size_mb = config.bot.MAX_FILE_SIZE / 1024 / 1024
            user_message = cls.ERROR_MESSAGES["file_too_large"].format(
                max_size=max_size_mb
            )
            
        elif "invalid file format" in str(error).lower() or "unsupported format" in str(error).lower():
            user_message = cls.ERROR_MESSAGES["invalid_file_format"].format(
                allowed_formats="PDF, DOC, DOCX, TXT"
            )
            
        else:
            user_message = f"❌ Ошибка при обработке {file_type}. Попробуйте другой файл."
            
        logger.warning(f"Ошибка файла ({file_type}): {error}")
        await cls._send_error_message(user_message, message)
    
    @classmethod
    async def handle_validation_error(
        cls,
        error: Exception,
        message: types.Message = None,
        callback: types.CallbackQuery = None,
        details: str = None
    ) -> None:
        """Обрабатывает ошибки валидации данных"""
        user_message = cls.ERROR_MESSAGES["validation_error"].format(
            details=details or str(error)
        )
        logger.warning(f"Ошибка валидации: {error}, details: {details}")
        await cls._send_error_message(user_message, message, callback)
    
    @classmethod
    async def handle_database_error(
        cls,
        error: Exception,
        message: types.Message = None,
        callback: types.CallbackQuery = None
    ) -> None:
        """Обрабатывает ошибки базы данных"""
        user_message = cls.ERROR_MESSAGES["database_error"]
        logger.error(f"Ошибка базы данных: {error}")
        await cls._send_error_message(user_message, message, callback)
    
    @classmethod
    async def handle_rate_limit(
        cls,
        message: types.Message = None,
        callback: types.CallbackQuery = None,
        cooldown: int = 30
    ) -> None:
        """Обрабатывает ограничение частоты запросов"""
        user_message = cls.ERROR_MESSAGES["rate_limit"].format(cooldown=cooldown)
        logger.info(f"Rate limit сработал для пользователя, cooldown: {cooldown}с")
        await cls._send_error_message(user_message, message, callback)
    
    @classmethod
    async def _send_error_message(
        cls,
        error_message: str,
        message: types.Message = None,
        callback: types.CallbackQuery = None
    ) -> None:
        """Отправляет сообщение об ошибке пользователю"""
        try:
            if callback:
                await callback.message.answer(error_message)
            elif message:
                await message.answer(error_message)
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    @classmethod
    def log_error_with_context(
        cls,
        error: Exception,
        context: Dict[str, Any] = None,
        level: str = "ERROR"
    ) -> None:
        """Логирует ошибку с дополнительным контекстом"""
        context_info = ""
        if context:
            context_info = " | Контекст: " + " | ".join(f"{k}={v}" for k, v in context.items())
        
        error_traceback = traceback.format_exc()
        
        log_message = f"Ошибка: {error}{context_info}\nТрассировка: {error_traceback}"
        
        if level.upper() == "CRITICAL":
            logger.critical(log_message)
        elif level.upper() == "WARNING":
            logger.warning(log_message)
        else:
            logger.error(log_message)


class SafeExecutor:
    """Класс для безопасного выполнения операций с обработкой ошибок"""
    
    @classmethod
    async def execute_with_retry(
        cls,
        operation,
        *args,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        error_message: str = None,
        message: types.Message = None,
        callback: types.CallbackQuery = None,
        **kwargs
    ) -> Any:
        """
        Выполняет операцию с повторными попытками при ошибках
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await operation(*args, **kwargs)
                return result
                
            except Exception as e:
                last_error = e
                
                # Пробуем обработать как Telegram ошибку
                if isinstance(e, TelegramAPIError):
                    handled = await ErrorHandler.handle_telegram_error(e, message, callback)
                    if not handled:
                        break
                        
                logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
            
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(retry_delay * (attempt + 1))  # Экспоненциальная задержка
        
        # Если все попытки не удались
        if error_message and (message or callback):
            await ErrorHandler._send_error_message(error_message, message, callback)
        
        ErrorHandler.log_error_with_context(
            last_error, 
            {"operation": operation.__name__, "max_retries": max_retries}
        )
        
        return None


# Глобальный экземпляр обработчика ошибок
error_handler = ErrorHandler()
safe_executor = SafeExecutor()

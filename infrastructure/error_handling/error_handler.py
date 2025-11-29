"""Base error handler."""
import logging
import traceback
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Base error handler with common functionality."""
    
    def __init__(self):
        self.known_errors: Dict[str, str] = {
            'network_error': '⚠️ Проблемы с сетью. Попробуйте позже.',
            'timeout_error': '⚠️ Время ожидания истекло. Попробуйте снова.',
            'validation_error': '⚠️ Ошибка в данных. Проверьте ввод.',
            'permission_error': '⚠️ Недостаточно прав для выполнения действия.',
            'unknown_error': '⚠️ Произошла непредвиденная ошибка.'
        }
    
    def get_user_message(self, error: Exception) -> str:
        """Get user-friendly error message."""
        error_type = type(error).__name__
        
        if 'timeout' in str(error).lower():
            return self.known_errors['timeout_error']
        elif 'network' in str(error).lower() or 'connection' in str(error).lower():
            return self.known_errors['network_error']
        elif 'validation' in str(error).lower():
            return self.known_errors['validation_error']
        elif 'permission' in str(error).lower() or 'forbidden' in str(error).lower():
            return self.known_errors['permission_error']
        else:
            return self.known_errors['unknown_error']
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        logger.error(f"❌ Error: {error_info['error_type']} - {error_info['error_message']}")
        logger.debug(f"🔍 Error details: {error_info}")
        
        if error_info['error_type'] not in ['TelegramBadRequest', 'ValidationError']:
            logger.error(f"📋 Traceback: {error_info['traceback']}")

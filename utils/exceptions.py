"""
Кастомные исключения для бота
"""

class DocumentBotError(Exception):
    """Базовое исключение для бота"""
    pass


class ValidationError(DocumentBotError):
    """Ошибка валидации данных"""
    pass


class FileProcessingError(DocumentBotError):
    """Ошибка обработки файла"""
    pass


class DatabaseError(DocumentBotError):
    """Ошибка базы данных"""
    pass


class PermissionDeniedError(DocumentBotError):
    """Ошибка прав доступа"""
    pass


class RateLimitError(DocumentBotError):
    """Ошибка превышения лимита запросов"""
    def __init__(self, cooldown: int = 30, message: str = None):
        self.cooldown = cooldown
        self.message = message
        super().__init__(message or f"Rate limit exceeded. Cooldown: {cooldown}s")

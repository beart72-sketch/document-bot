class LegalBotException(Exception):
    """Базовое исключение для юридического бота"""
    pass

class DomainException(LegalBotException):
    """Исключения доменного уровня"""
    pass

class InfrastructureException(LegalBotException):
    """Исключения инфраструктурного уровня"""
    pass

class ApplicationException(LegalBotException):
    """Исключения уровня приложения"""
    pass

# Доменные исключения
class UserNotFoundError(DomainException):
    """Пользователь не найден"""
    pass

class DocumentNotFoundError(DomainException):
    """Документ не найден"""
    pass

class SubscriptionError(DomainException):
    """Ошибка подписки"""
    pass

class TemplateNotFoundError(DomainException):
    """Шаблон не найден"""
    pass

class ValidationError(DomainException):
    """Ошибка валидации"""
    pass

# Инфраструктурные исключения
class DatabaseError(InfrastructureException):
    """Ошибка базы данных"""
    pass

class CacheError(InfrastructureException):
    """Ошибка кэширования"""
    pass

class AIAnalysisError(InfrastructureException):
    """Ошибка AI анализа"""
    pass

# Прикладные исключения
class UseCaseError(ApplicationException):
    """Ошибка use case"""
    pass

class AccessDeniedError(ApplicationException):
    """Доступ запрещен"""
    pass

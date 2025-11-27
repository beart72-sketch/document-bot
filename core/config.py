import os
from pathlib import Path

class Config:
    """Конфигурация бота"""
    TOKEN = "8446758342:AAEr16cvfHHLyYBh02-jGl-UTbgJKNPD7HE"
    ADMIN_IDS = [123456789]
    DB_NAME = "legal_bot.db"
    BACKUP_DIR = "backups"
    LOGS_DIR = "logs"
    ENCRYPTION_KEY = "секрет"
    SALT = b"legal_bot_salt_2024"
    
    # Пути
    TEMPLATES_DIR: Path = Path("templates")
    
    # Таймауты кэширования
    USER_CACHE_TIMEOUT: int = 300  # 5 минут
    AI_CACHE_TIMEOUT: int = 600    # 10 минут
    
    # Базовые лимиты
    FREE_DOCUMENTS_PER_MONTH: int = 5
    FREE_AI_REQUESTS: int = 10

# Экспортируем конфигурацию
config = Config()

import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """Конфигурация базы данных"""
    
    def __init__(self):
        self.DB_NAME = os.getenv("DB_NAME", "document_bot.db")
        self.DB_URL = f"sqlite+aiosqlite:///{self.DB_NAME}"
        self.MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "10"))
        self.MIN_CONNECTIONS = int(os.getenv("MIN_CONNECTIONS", "2"))
    
    def validate(self) -> List[str]:
        """Проверка настроек базы данных"""
        errors = []
        
        if not self.DB_NAME:
            errors.append("Имя базы данных не указано (DB_NAME)")
        
        if not self.DB_URL.startswith(('sqlite+aiosqlite:///', 'postgresql+asyncpg://', 'mysql+aiomysql://')):
            errors.append(f"Неподдерживаемый формат URL базы данных: {self.DB_URL}")
            
        return errors


class BotConfig:
    """Конфигурация бота"""
    
    def __init__(self):
        self.TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.ADMIN_IDS = self._parse_admin_ids()
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "52428800"))
        self.MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
        self.RATE_LIMIT_PER_USER = int(os.getenv("RATE_LIMIT_PER_USER", "10"))
    
    def _parse_admin_ids(self) -> List[int]:
        """Парсит список ID администраторов"""
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if not admin_ids_str.strip():
            return []
        
        admin_ids = []
        for admin_id in admin_ids_str.split(","):
            try:
                admin_ids.append(int(admin_id.strip()))
            except ValueError:
                print(f"⚠️  Некорректный ID администратора: {admin_id}")
        
        return admin_ids
    
    def validate(self) -> List[str]:
        """Проверка настроек бота"""
        errors = []
        
        if not self.TOKEN:
            errors.append("Токен бота не установлен (TELEGRAM_BOT_TOKEN)")
        elif not self.TOKEN.count(':') == 1:
            errors.append("Неверный формат токена бота")
        
        if not self.ADMIN_IDS:
            errors.append("Не указаны ID администраторов (ADMIN_IDS)")
        
        return errors


class SecurityConfig:
    """Конфигурация безопасности"""
    
    def __init__(self):
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "dev_encryption_key_change_in_production")
        self.SALT = os.getenv("SALT", "document_bot_salt_2024").encode()
    
    def validate(self) -> List[str]:
        """Проверка настроек безопасности"""
        errors = []
        
        if self.ENCRYPTION_KEY == "dev_encryption_key_change_in_production":
            errors.append("⚠️  Используется ключ шифрования по умолчанию")
        
        return errors


class LoggingConfig:
    """Конфигурация логирования"""
    
    def __init__(self):
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOGS_DIR = os.getenv("LOGS_DIR", "logs")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"
        os.makedirs(self.LOGS_DIR, exist_ok=True)
    
    def validate(self) -> List[str]:
        """Проверка настроек логирования"""
        errors = []
        
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL.upper() not in valid_levels:
            errors.append(f"LOG_LEVEL должен быть одним из: {', '.join(valid_levels)}")
        
        return errors


class StorageConfig:
    """Конфигурация хранилища"""
    
    def __init__(self):
        self.BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
        self.DEFAULT_DOCUMENT_LIMIT = int(os.getenv("DEFAULT_DOCUMENT_LIMIT", "5"))
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
    
    def validate(self) -> List[str]:
        """Проверка настроек хранилища"""
        return []


class Config:
    """Основной класс конфигурации приложения"""
    
    def __init__(self):
        self.APP_NAME = "Document Bot"
        self.APP_VERSION = "1.0.0"
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        
        self.database = DatabaseConfig()
        self.bot = BotConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self.storage = StorageConfig()
    
    def validate(self) -> List[str]:
        """Полная проверка всей конфигурации"""
        errors = []
        errors.extend(self.database.validate())
        errors.extend(self.bot.validate())
        errors.extend(self.security.validate())
        errors.extend(self.logging.validate())
        errors.extend(self.storage.validate())
        return errors
    
    def get_admin_ids(self) -> List[int]:
        return self.bot.ADMIN_IDS
    
    def get_bot_token(self) -> str:
        return self.bot.TOKEN


config = Config()

def print_config_summary():
    print(f"=== Конфигурация {config.APP_NAME} v{config.APP_VERSION} ===")
    print(f"Режим отладки: {'ВКЛ' if config.DEBUG else 'ВЫКЛ'}")
    print(f"Уровень логирования: {config.logging.LOG_LEVEL}")
    print(f"Администраторы: {len(config.get_admin_ids())}")
    print(f"База данных: {config.database.DB_NAME}")

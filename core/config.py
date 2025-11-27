import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация бота"""
    TOKEN = "8446758342:AAEr16cvfHHLyYBh02-jGl-UTbgJKNPD7HE"
    ADMIN_IDS = [123456789]
    DB_NAME = "legal_bot.db"
    BACKUP_DIR = "backups"
    LOGS_DIR = "logs"
    ENCRYPTION_KEY = "секрет"
    SALT = b"legal_bot_salt_2024"

# Для совместимости с существующим кодом создаем dataclass конфиг
@dataclass
class TelegramConfig:
    bot_token: str = Config.TOKEN
    admin_ids: List[int] = field(default_factory=lambda: Config.ADMIN_IDS)

@dataclass
class DatabaseConfig:
    database: str = Config.DB_NAME
    
    @property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self.database}"

@dataclass
class AppConfig:
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)

# Глобальный экземпляр конфигурации
config = AppConfig()

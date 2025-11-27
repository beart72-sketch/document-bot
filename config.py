import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация бота"""

    # Токен бота из переменных окружения
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # ID администраторов (можно указать несколько через запятую в .env)
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

    # Настройки базы данных
    DB_NAME = os.getenv("DB_NAME", "legal_bot.db")
    DB_URL = f"sqlite+aiosqlite:///{DB_NAME}"

    # Директории
    BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
    LOGS_DIR = os.getenv("LOGS_DIR", "logs")

    # Создаем необходимые директории
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Настройки шифрования (для production использовать внешние секреты)
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "dev_encryption_key_change_in_production")
    SALT = os.getenv("SALT", "legal_bot_salt_2024").encode()

    # Лимиты по умолчанию
    DEFAULT_DOCUMENT_LIMIT = 5
    DEFAULT_AI_REQUESTS = 10

    # Настройки логирования
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """Проверка конфигурации"""
        errors = []

        if not cls.TOKEN:
            errors.append("Токен бота не установлен (TELEGRAM_BOT_TOKEN)")

        if not cls.ADMIN_IDS:
            errors.append("Не указаны ID администраторов (ADMIN_IDS)")

        if cls.ENCRYPTION_KEY == "dev_encryption_key_change_in_production":
            print("⚠️  ВНИМАНИЕ: Используется ключ шифрования по умолчанию. Для production измените ENCRYPTION_KEY")

        return errors

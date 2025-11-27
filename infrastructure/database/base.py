from sqlalchemy.ext.declarative import declarative_base

# Создаем базовый класс для всех моделей
Base = declarative_base()

# Экспортируем его для использования в других файлах
__all__ = ['Base']

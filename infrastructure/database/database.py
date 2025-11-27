from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .base import Base  # Импортируем Base из нового файла

class Database:
    def __init__(self):
        self.engine = None
        self.async_session = None
    
    async def initialize(self):
        """Инициализация базы данных"""
        # Используем SQLite для простоты
        database_url = "sqlite+aiosqlite:///legal_bot.db"
        
        self.engine = create_async_engine(
            database_url,
            echo=True,
            future=True
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Создаем таблицы
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self) -> AsyncSession:
        """Получение сессии базы данных"""
        async with self.async_session() as session:
            yield session
    
    async def close(self):
        """Закрытие соединения с базой данных"""
        if self.engine:
            await self.engine.dispose()

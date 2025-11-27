from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from core.config import load_config
from infrastructure.database.models import Base

class Database:
    """Асинхронная база данных SQLAlchemy 2.0+"""
    
    def __init__(self):
        self.config = load_config()
        self.engine = create_async_engine(
            self.config.database_url,
            echo=self.config.database_echo,
            pool_pre_ping=self.config.database_pool_pre_ping
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Создает все таблицы в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Удаляет все таблицы из базы данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def get_session(self) -> AsyncSession:
        """Возвращает асинхронную сессию"""
        return self.async_session_maker()
    
    async def health_check(self) -> bool:
        """Проверяет подключение к базе данных"""
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

# Глобальный экземпляр для обратной совместимости
database = Database()

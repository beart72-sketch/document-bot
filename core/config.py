from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Bot settings
    bot_token: str
    admin_ids: List[int] = [123456789]
    
    # Database settings
    database_url: str = "sqlite+aiosqlite:///legal_bot.db"
    database_echo: bool = False
    database_pool_pre_ping: bool = True
    
    class Config:
        env_file = ".env"

def load_config() -> Settings:
    return Settings()

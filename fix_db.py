from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100))
    role = Column(String(50), default='user')
    subscription_type = Column(String(50))
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    is_subscription_active = Column(Boolean, default=False)
    settings = Column(Text)
    last_activity = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Создать все таблицы
engine = create_engine('sqlite:///your_database.db')
Base.metadata.create_all(engine)
print("Таблицы успешно созданы!")

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum
from datetime import datetime
from .base import Base
import enum

class SubscriptionPlan(enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    BUSINESS = "business"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    role = Column(String(50), default="user")
    subscription_type = Column(String(50), default="free")
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    is_subscription_active = Column(Boolean, default=False)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentModel(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String(255))
    content = Column(Text)
    document_type = Column(String(50))
    status = Column(String(50))
    user_id = Column(String, index=True)
    template_id = Column(String)
    document_metadata = Column(JSON)
    variables = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SubscriptionModel(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    plan = Column(SQLEnum(SubscriptionPlan))
    status = Column(SQLEnum(SubscriptionStatus))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    features = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentTemplateModel(Base):
    __tablename__ = "document_templates"
    
    id = Column(String, primary_key=True)
    name = Column(String(255))
    description = Column(Text)
    content = Column(Text)
    document_type = Column(String(100))
    variables_schema = Column(JSON)
    required_variables = Column(JSON)
    category = Column(String(100), default="general")
    version = Column(String(50), default="1.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class DocumentStatus(enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class DocumentType(enum.Enum):
    CLAIM = "claim"
    CONTRACT = "contract"
    COMPLAINT = "complaint"
    MOTION = "motion"

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
    document_type = Column(SQLEnum(DocumentType))
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    user_id = Column(String, index=True)
    template_id = Column(String)
    document_metadata = Column(JSON)  # Изменяем с metadata на document_metadata
    variables = Column(JSON)
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

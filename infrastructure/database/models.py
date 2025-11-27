from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, Integer, BigInteger, Boolean, JSON, ForeignKey
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")
    subscription_type: Mapped[str] = mapped_column(String(50), default="free")
    subscription_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    subscription_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_subscription_active: Mapped[bool] = mapped_column(Boolean, default=False)
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    documents: Mapped[list["DocumentModel"]] = relationship("DocumentModel", back_populates="user")

class DocumentTemplateModel(Base):
    __tablename__ = "document_templates"
    
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    variables_schema: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    required_variables: Mapped[list] = mapped_column(JSON, default=list)
    category: Mapped[str] = mapped_column(String(100), default="general")
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    documents: Mapped[list["DocumentModel"]] = relationship("DocumentModel", back_populates="template")

class DocumentModel(Base):
    __tablename__ = "documents"
    
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    
    # Внешние ключи
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    template_id: Mapped[Optional[str]] = mapped_column(ForeignKey("document_templates.id"))
    
    # Метаданные (переименовано из metadata в document_metadata)
    document_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    variables: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="documents")
    template: Mapped[Optional["DocumentTemplateModel"]] = relationship("DocumentTemplateModel", back_populates="documents")

from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    profile_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    template_id = Column(String, nullable=True)
    document_metadata = Column(JSON, nullable=True)
    variables = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    plan = Column(String, nullable=False)
    status = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    features = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

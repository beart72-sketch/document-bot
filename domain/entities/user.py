from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4

@dataclass
class User:
    """Доменная модель пользователя"""
    id: Optional[str] = None
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role: str = "user"
    subscription_type: str = "free"
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    is_subscription_active: bool = False
    settings: Dict[str, Any] = None
    last_activity: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    documents: List['Document'] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())
        if self.settings is None:
            self.settings = {}
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.documents is None:
            self.documents = []
    
    def update_activity(self) -> None:
        """Обновляет время последней активности"""
        self.last_activity = datetime.utcnow()
    
    def can_create_document(self) -> bool:
        """Проверяет, может ли пользователь создавать документы"""
        if self.subscription_type == "premium":
            return True
        # Для free пользователей проверяем лимиты
        return len(self.documents) < 5
    
    def get_document_count(self) -> int:
        """Возвращает количество документов пользователя"""
        return len(self.documents)
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, telegram_id={self.telegram_id}, username=@{self.username})"

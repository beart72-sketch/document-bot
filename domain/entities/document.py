from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from enum import Enum

class DocumentStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class DocumentType(Enum):
    CLAIM = "claim"  # Исковое заявление
    CONTRACT = "contract"  # Договор
    COMPLAINT = "complaint"  # Жалоба
    MOTION = "motion"  # Ходатайство

@dataclass
class Document:
    """Доменная модель документа"""
    id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: DocumentStatus = DocumentStatus.DRAFT
    user_id: Optional[str] = None
    template_id: Optional[str] = None
    document_metadata: Dict[str, Any] = None
    variables: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())
        if self.document_metadata is None:
            self.document_metadata = {}
        if self.variables is None:
            self.variables = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Свойство для доступа к document_metadata"""
        return self.document_metadata
    
    @metadata.setter
    def metadata(self, value: Dict[str, Any]) -> None:
        """Сеттер для document_metadata"""
        self.document_metadata = value
    
    def update_content(self, new_content: str) -> None:
        """Обновляет содержимое документа"""
        self.content = new_content
        self.updated_at = datetime.utcnow()
    
    def change_status(self, new_status: DocumentStatus) -> None:
        """Изменяет статус документа"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"Document(id={self.id}, title='{self.title}', type={self.document_type})"

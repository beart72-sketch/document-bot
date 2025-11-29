from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from domain.models.document import Document, DocumentStatus, DocumentType

class CreateDocumentRequest(BaseModel):
    user_telegram_id: int
    title: str
    document_type: DocumentType
    content: Optional[str] = None
    template_id: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    document_type: str
    status: str
    user_id: str
    template_id: Optional[str]
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_domain(cls, document: Document) -> 'DocumentResponse':
        return cls(
            id=document.id,
            title=document.title,
            content=document.content,
            document_type=document.document_type.value,
            status=document.status.value,
            user_id=document.user_id,
            template_id=document.template_id,
            variables=document.variables,
            metadata=document.metadata,
            created_at=document.created_at,
            updated_at=document.updated_at
        )

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total_count: int
    user_document_limit: int

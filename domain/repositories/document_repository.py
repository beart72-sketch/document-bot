from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.document import Document, DocumentStatus, DocumentType

class DocumentRepository(ABC):
    """Порт для репозитория документов"""
    
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Document]:
        pass
    
    @abstractmethod
    async def create(self, document: Document) -> Document:
        pass
    
    @abstractmethod
    async def update(self, document: Document) -> Document:
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_by_status(self, user_id: str, status: DocumentStatus) -> List[Document]:
        pass
    
    @abstractmethod
    async def get_by_type(self, user_id: str, doc_type: DocumentType) -> List[Document]:
        pass

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models.document import Document

class DocumentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Document]:
        pass

    @abstractmethod
    async def get_by_status(self, status: str) -> List[Document]:
        pass

    @abstractmethod
    async def get_by_type(self, doc_type: str) -> List[Document]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Document]:
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

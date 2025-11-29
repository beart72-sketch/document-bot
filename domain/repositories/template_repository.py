from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models.document_template import DocumentTemplate

class TemplateRepository(ABC):
    """Порт для репозитория шаблонов"""
    
    @abstractmethod
    async def get_by_id(self, template_id: str) -> Optional[DocumentTemplate]:
        pass
    
    @abstractmethod
    async def get_all_active(self) -> List[DocumentTemplate]:
        pass
    
    @abstractmethod
    async def get_by_type(self, doc_type: str) -> List[DocumentTemplate]:
        pass
    
    @abstractmethod
    async def get_by_category(self, category: str) -> List[DocumentTemplate]:
        pass
    
    @abstractmethod
    async def create(self, template: DocumentTemplate) -> DocumentTemplate:
        pass

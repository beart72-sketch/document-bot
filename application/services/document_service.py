import logging
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
from domain.models.document import Document, DocumentStatus, DocumentType
from domain.repositories.document_repository import DocumentRepository
from application.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, document_repo: DocumentRepository, subscription_service: SubscriptionService):
        self.document_repo = document_repo
        self.subscription_service = subscription_service
    
    async def create_document(self, 
                           user_id: str,
                           title: str,
                           content: str,
                           document_type: str,
                           template_id: Optional[str] = None,
                           variables: Optional[Dict[str, Any]] = None) -> Document:
        try:
            # Проверяем лимит документов
            user_documents = await self.document_repo.get_by_user_id(user_id)
            current_month_docs = self._count_current_month_documents(user_documents)
            
            can_create = await self.subscription_service.check_document_limit(user_id, current_month_docs)
            if not can_create:
                raise Exception("❌ Превышен лимит документов для вашей подписки")
            
            # Создаем документ
            document = Document(
                id=str(uuid4()),
                title=title,
                content=content,
                document_type=document_type,
                status=DocumentStatus.DRAFT.value,
                user_id=user_id,
                template_id=template_id,
                variables=variables or {},
                document_metadata={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return await self.document_repo.create(document)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания документа: {e}")
            raise
    
    async def get_user_documents(self, user_id: str) -> List[Document]:
        try:
            documents = await self.document_repo.get_by_user_id(user_id)
            logger.info(f"📋 Найдено {len(documents)} документов для пользователя {user_id}")
            return documents
        except Exception as e:
            logger.error(f"❌ Ошибка получения документов пользователя: {e}")
            return []
    
    async def update_document_status(self, document_id: str, status: str) -> Optional[Document]:
        try:
            document = await self.document_repo.get_by_id(document_id)
            if document:
                document.status = status
                document.updated_at = datetime.utcnow()
                return await self.document_repo.update(document)
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка обновления статуса документа: {e}")
            return None
    
    async def get_document_stats(self, user_id: str) -> Dict[str, Any]:
        try:
            documents = await self.document_repo.get_by_user_id(user_id)
            total_docs = len(documents)
            
            status_stats = {}
            type_stats = {}
            
            for doc in documents:
                status_stats[doc.status] = status_stats.get(doc.status, 0) + 1
                type_stats[doc.document_type] = type_stats.get(doc.document_type, 0) + 1
            
            current_month_docs = self._count_current_month_documents(documents)
            remaining_docs = await self.subscription_service.get_remaining_documents(user_id, current_month_docs)
            
            return {
                "total_documents": total_docs,
                "current_month_documents": current_month_docs,
                "remaining_documents": remaining_docs,
                "status_distribution": status_stats,
                "type_distribution": type_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики документов: {e}")
            return {
                "total_documents": 0,
                "current_month_documents": 0,
                "remaining_documents": 0,
                "status_distribution": {},
                "type_distribution": {}
            }
    
    def _count_current_month_documents(self, documents: List[Document]) -> int:
        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year
        
        count = 0
        for doc in documents:
            if doc.created_at and doc.created_at.month == current_month and doc.created_at.year == current_year:
                count += 1
        return count

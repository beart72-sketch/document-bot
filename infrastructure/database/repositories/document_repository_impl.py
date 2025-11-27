from typing import Optional, List
import logging
from domain.entities.document import Document, DocumentStatus, DocumentType
from domain.repositories.document_repository import DocumentRepository
from infrastructure.database.models import DocumentModel
from sqlalchemy import select

logger = logging.getLogger(__name__)

class DocumentRepositoryImpl(DocumentRepository):
    def __init__(self, database):
        self.database = database
    
    async def get_by_user_id(self, user_id: str) -> List[Document]:
        """Получает документы пользователя"""
        try:
            async with self.database.async_session() as session:
                stmt = select(DocumentModel).where(DocumentModel.user_id == user_id)
                result = await session.execute(stmt)
                documents = result.scalars().all()
                
                logger.info(f"Найдено {len(documents)} документов для user_id: {user_id}")
                
                result_docs = []
                for doc_model in documents:
                    try:
                        entity = self._to_entity(doc_model)
                        result_docs.append(entity)
                    except Exception as e:
                        logger.error(f"Ошибка конвертации документа {doc_model.id}: {e}")
                        # Создаем базовый документ чтобы не падать полностью
                        result_docs.append(Document(
                            id=doc_model.id,
                            title=doc_model.title or "Документ",
                            status=DocumentStatus.DRAFT,
                            user_id=doc_model.user_id
                        ))
                
                return result_docs
                
        except Exception as e:
            logger.error(f"Ошибка при получении документов для user_id {user_id}: {e}")
            return []
    
    def _to_entity(self, model: DocumentModel) -> Document:
        """Конвертирует модель БД в доменную сущность"""
        # Простая и надежная конвертация через mapping
        type_mapping = {
            'claim': DocumentType.CLAIM,
            'contract': DocumentType.CONTRACT, 
            'complaint': DocumentType.COMPLAINT,
            'motion': DocumentType.MOTION
        }
        
        status_mapping = {
            'draft': DocumentStatus.DRAFT,
            'in_progress': DocumentStatus.IN_PROGRESS,
            'completed': DocumentStatus.COMPLETED,
            'archived': DocumentStatus.ARCHIVED
        }
        
        doc_type = type_mapping.get(str(model.document_type).lower()) if model.document_type else None
        status = status_mapping.get(str(model.status).lower(), DocumentStatus.DRAFT)
        
        return Document(
            id=model.id,
            title=model.title,
            content=model.content,
            document_type=doc_type,
            status=status,
            user_id=model.user_id,
            template_id=model.template_id,
            document_metadata=model.document_metadata or {},
            variables=model.variables or {},
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    # Остальные методы...
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        async with self.database.async_session() as session:
            result = await session.get(DocumentModel, document_id)
            if result:
                return self._to_entity(result)
            return None
    
    async def get_by_status(self, status: DocumentStatus) -> List[Document]:
        async with self.database.async_session() as session:
            stmt = select(DocumentModel).where(DocumentModel.status == status.value)
            result = await session.execute(stmt)
            documents = result.scalars().all()
            return [self._to_entity(doc) for doc in documents]
    
    async def get_by_type(self, doc_type: DocumentType) -> List[Document]:
        async with self.database.async_session() as session:
            stmt = select(DocumentModel).where(DocumentModel.document_type == doc_type.value)
            result = await session.execute(stmt)
            documents = result.scalars().all()
            return [self._to_entity(doc) for doc in documents]
    
    async def get_all(self) -> List[Document]:
        async with self.database.async_session() as session:
            stmt = select(DocumentModel)
            result = await session.execute(stmt)
            documents = result.scalars().all()
            return [self._to_entity(doc) for doc in documents]
    
    async def create(self, document: Document) -> Document:
        async with self.database.async_session() as session:
            document_model = DocumentModel(
                id=document.id,
                title=document.title,
                content=document.content,
                document_type=document.document_type.value if document.document_type else None,
                status=document.status.value,
                user_id=document.user_id,
                template_id=document.template_id,
                document_metadata=document.document_metadata,
                variables=document.variables,
                created_at=document.created_at,
                updated_at=document.updated_at
            )
            session.add(document_model)
            await session.commit()
            return document
    
    async def update(self, document: Document) -> Document:
        async with self.database.async_session() as session:
            document_model = await session.get(DocumentModel, document.id)
            if document_model:
                document_model.title = document.title
                document_model.content = document.content
                document_model.document_type = document.document_type.value if document.document_type else None
                document_model.status = document.status.value
                document_model.document_metadata = document.document_metadata
                document_model.variables = document.variables
                document_model.updated_at = document.updated_at
                await session.commit()
            return document
    
    async def delete(self, document_id: str) -> bool:
        async with self.database.async_session() as session:
            document_model = await session.get(DocumentModel, document_id)
            if document_model:
                await session.delete(document_model)
                await session.commit()
                return True
            return False

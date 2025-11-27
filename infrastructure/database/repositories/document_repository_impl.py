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
            logger.info(f"🔍 Поиск документов для user_id: {user_id}")
            
            async with self.database.async_session() as session:
                stmt = select(DocumentModel).where(DocumentModel.user_id == user_id)
                result = await session.execute(stmt)
                documents = result.scalars().all()
                
                logger.info(f"📄 Найдено {len(documents)} документов в БД")
                
                result_docs = []
                for doc_model in documents:
                    try:
                        entity = self._to_entity(doc_model)
                        result_docs.append(entity)
                        logger.info(f"✅ Успешно сконвертирован документ: {entity.title}")
                    except Exception as e:
                        logger.error(f"❌ Ошибка конвертации документа {doc_model.id}: {e}")
                        # Создаем базовый документ чтобы не падать полностью
                        basic_doc = Document(
                            id=doc_model.id,
                            title=doc_model.title or "Документ",
                            status=DocumentStatus.DRAFT,
                            user_id=doc_model.user_id
                        )
                        result_docs.append(basic_doc)
                
                return result_docs
                
        except Exception as e:
            logger.error(f"💥 Критическая ошибка при получении документов для user_id {user_id}: {e}")
            return []
    
    def _to_entity(self, model: DocumentModel) -> Document:
        """
        АБСОЛЮТНО НАДЕЖНАЯ конвертация модели SQLAlchemy в сущность Document
        """
        # ЖЕСТКИЙ МАППИНГ значений из БД в enum
        DOCUMENT_TYPE_MAPPING = {
            # Все возможные варианты из базы данных
            'claim': DocumentType.CLAIM,
            'contract': DocumentType.CONTRACT,
            'complaint': DocumentType.COMPLAINT,
            'motion': DocumentType.MOTION,
            # Верхний регистр на всякий случай
            'CLAIM': DocumentType.CLAIM,
            'CONTRACT': DocumentType.CONTRACT,
            'COMPLAINT': DocumentType.COMPLAINT,
            'MOTION': DocumentType.MOTION,
            # Русские названия (если вдруг)
            'иск': DocumentType.CLAIM,
            'договор': DocumentType.CONTRACT,
            'жалоба': DocumentType.COMPLAINT,
            'ходатайство': DocumentType.MOTION
        }
        
        STATUS_MAPPING = {
            'draft': DocumentStatus.DRAFT,
            'in_progress': DocumentStatus.IN_PROGRESS,
            'completed': DocumentStatus.COMPLETED,
            'archived': DocumentStatus.ARCHIVED,
            # Верхний регистр
            'DRAFT': DocumentStatus.DRAFT,
            'IN_PROGRESS': DocumentStatus.IN_PROGRESS,
            'COMPLETED': DocumentStatus.COMPLETED,
            'ARCHIVED': DocumentStatus.ARCHIVED
        }
        
        # Конвертация document_type
        doc_type = None
        if model.document_type:
            type_str = str(model.document_type).strip()
            doc_type = DOCUMENT_TYPE_MAPPING.get(type_str)
            
            if not doc_type:
                # Пробуем найти без учета регистра
                type_lower = type_str.lower()
                for key, value in DOCUMENT_TYPE_MAPPING.items():
                    if key.lower() == type_lower:
                        doc_type = value
                        break
            
            if not doc_type:
                logger.warning(f"⚠️ Неизвестный тип документа: '{type_str}', использую CLAIM по умолчанию")
                doc_type = DocumentType.CLAIM
        
        # Конвертация status
        status = DocumentStatus.DRAFT
        if model.status:
            status_str = str(model.status).strip()
            status = STATUS_MAPPING.get(status_str)
            
            if not status:
                # Пробуем найти без учета регистра
                status_lower = status_str.lower()
                for key, value in STATUS_MAPPING.items():
                    if key.lower() == status_lower:
                        status = value
                        break
            
            if not status:
                logger.warning(f"⚠️ Неизвестный статус: '{status_str}', использую DRAFT по умолчанию")
                status = DocumentStatus.DRAFT
        
        logger.info(f"🔄 Конвертация: '{model.document_type}' -> {doc_type}, '{model.status}' -> {status}")
        
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

    # Остальные методы остаются без изменений...
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

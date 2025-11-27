from typing import Optional, List
import logging
from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository
from infrastructure.database.models import DocumentModel
from sqlalchemy import select

logger = logging.getLogger(__name__)

class DocumentRepositoryImpl(DocumentRepository):
    def __init__(self, database):
        self.database = database
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        try:
            async with self.database.async_session() as session:
                result = await session.get(DocumentModel, document_id)
                if result:
                    return self._to_entity(result)
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения документа по ID {document_id}: {e}")
            return None
    
    async def get_by_user_id(self, user_id: str) -> List[Document]:
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
                        basic_doc = Document(
                            id=doc_model.id,
                            title=doc_model.title or "Документ",
                            content=doc_model.content or "",
                            document_type=doc_model.document_type or "claim",
                            status=doc_model.status or "draft",
                            user_id=doc_model.user_id
                        )
                        result_docs.append(basic_doc)

                logger.info(f"📋 Итоговый список документов: {len(result_docs)}")
                return result_docs

        except Exception as e:
            logger.error(f"💥 Критическая ошибка при получении документов для user_id {user_id}: {e}")
            return []

    def _to_entity(self, model: DocumentModel) -> Document:
        try:
            return Document(
                id=model.id,
                title=model.title or "Без названия",
                content=model.content or "",
                document_type=model.document_type or "claim",
                status=model.status or "draft",
                user_id=model.user_id,
                template_id=model.template_id,
                document_metadata=model.document_metadata or {},
                variables=model.variables or {},
                created_at=model.created_at,
                updated_at=model.updated_at
            )
        except Exception as e:
            logger.error(f"❌ Ошибка конвертации документа {model.id}: {e}")
            raise

    async def get_by_status(self, status: str) -> List[Document]:
        async with self.database.async_session() as session:
            stmt = select(DocumentModel).where(DocumentModel.status == status)
            result = await session.execute(stmt)
            documents = result.scalars().all()
            return [self._to_entity(doc) for doc in documents]

    async def get_by_type(self, doc_type: str) -> List[Document]:
        async with self.database.async_session() as session:
            stmt = select(DocumentModel).where(DocumentModel.document_type == doc_type)
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
                document_type=document.document_type,
                status=document.status,
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
                document_model.document_type = document.document_type
                document_model.status = document.status
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

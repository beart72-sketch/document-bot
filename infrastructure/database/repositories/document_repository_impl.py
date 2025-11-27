from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from domain.repositories.document_repository import DocumentRepository
from domain.entities.document import Document, DocumentStatus, DocumentType
from infrastructure.database.models import DocumentModel

class DocumentRepositoryImpl(DocumentRepository):
    """Реализация репозитория документов на SQLAlchemy 2.0+"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        result = await self._session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        db_document = result.scalar_one_or_none()
        return self._to_domain(db_document) if db_document else None
    
    async def get_by_user_id(self, user_id: str) -> List[Document]:
        result = await self._session.execute(
            select(DocumentModel).where(DocumentModel.user_id == user_id)
        )
        return [self._to_domain(db_doc) for db_doc in result.scalars().all()]
    
    async def create(self, document: Document) -> Document:
        db_document = DocumentModel(
            title=document.title,
            content=document.content,
            document_type=document.document_type.value,
            status=document.status.value,
            user_id=document.user_id,
            template_id=document.template_id,
            document_metadata=document.metadata,
            variables=document.variables
        )
        self._session.add(db_document)
        await self._session.commit()
        await self._session.refresh(db_document)
        return self._to_domain(db_document)
    
    async def update(self, document: Document) -> Document:
        db_document = await self._session.get(DocumentModel, document.id)
        if db_document:
            db_document.title = document.title
            db_document.content = document.content
            db_document.document_type = document.document_type.value
            db_document.status = document.status.value
            db_document.document_metadata = document.metadata
            db_document.variables = document.variables
            await self._session.commit()
            return self._to_domain(db_document)
        return None
    
    async def delete(self, document_id: str) -> bool:
        result = await self._session.execute(
            delete(DocumentModel).where(DocumentModel.id == document_id)
        )
        await self._session.commit()
        return result.rowcount > 0
    
    async def get_by_status(self, user_id: str, status: DocumentStatus) -> List[Document]:
        result = await self._session.execute(
            select(DocumentModel)
            .where(
                DocumentModel.user_id == user_id,
                DocumentModel.status == status.value
            )
        )
        return [self._to_domain(db_doc) for db_doc in result.scalars().all()]
    
    async def get_by_type(self, user_id: str, doc_type: DocumentType) -> List[Document]:
        result = await self._session.execute(
            select(DocumentModel)
            .where(
                DocumentModel.user_id == user_id,
                DocumentModel.document_type == doc_type.value
            )
        )
        return [self._to_domain(db_doc) for db_doc in result.scalars().all()]
    
    def _to_domain(self, db_document: DocumentModel) -> Document:
        """Преобразует модель БД в доменную модель"""
        return Document(
            id=db_document.id,
            title=db_document.title,
            content=db_document.content,
            document_type=DocumentType(db_document.document_type),
            status=DocumentStatus(db_document.status),
            user_id=db_document.user_id,
            template_id=db_document.template_id,
            variables=db_document.variables,
            document_metadata=db_document.document_metadata,
            created_at=db_document.created_at,
            updated_at=db_document.updated_at
        )

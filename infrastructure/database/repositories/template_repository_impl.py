from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from domain.repositories.template_repository import TemplateRepository
from domain.entities.document_template import DocumentTemplate
from infrastructure.database.models import DocumentTemplateModel

class TemplateRepositoryImpl(TemplateRepository):
    """Реализация репозитория шаблонов на SQLAlchemy 2.0+"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, template_id: str) -> Optional[DocumentTemplate]:
        result = await self._session.execute(
            select(DocumentTemplateModel).where(DocumentTemplateModel.id == template_id)
        )
        db_template = result.scalar_one_or_none()
        return self._to_domain(db_template) if db_template else None
    
    async def get_all_active(self) -> List[DocumentTemplate]:
        result = await self._session.execute(
            select(DocumentTemplateModel).where(DocumentTemplateModel.is_active == True)
        )
        return [self._to_domain(db_tpl) for db_tpl in result.scalars().all()]
    
    async def get_by_type(self, doc_type: str) -> List[DocumentTemplate]:
        result = await self._session.execute(
            select(DocumentTemplateModel)
            .where(
                DocumentTemplateModel.document_type == doc_type,
                DocumentTemplateModel.is_active == True
            )
        )
        return [self._to_domain(db_tpl) for db_tpl in result.scalars().all()]
    
    async def get_by_category(self, category: str) -> List[DocumentTemplate]:
        result = await self._session.execute(
            select(DocumentTemplateModel)
            .where(
                DocumentTemplateModel.category == category,
                DocumentTemplateModel.is_active == True
            )
        )
        return [self._to_domain(db_tpl) for db_tpl in result.scalars().all()]
    
    async def create(self, template: DocumentTemplate) -> DocumentTemplate:
        db_template = DocumentTemplateModel(
            name=template.name,
            description=template.description,
            content=template.content,
            document_type=template.document_type,
            variables_schema=template.variables_schema,
            required_variables=template.required_variables,
            category=template.category,
            version=template.version,
            is_active=template.is_active
        )
        self._session.add(db_template)
        await self._session.commit()
        await self._session.refresh(db_template)
        return self._to_domain(db_template)
    
    def _to_domain(self, db_template: DocumentTemplateModel) -> DocumentTemplate:
        """Преобразует модель БД в доменную модель"""
        return DocumentTemplate(
            id=db_template.id,
            name=db_template.name,
            description=db_template.description,
            content=db_template.content,
            document_type=db_template.document_type,
            variables_schema=db_template.variables_schema,
            required_variables=db_template.required_variables,
            category=db_template.category,
            version=db_template.version,
            is_active=db_template.is_active,
            created_at=db_template.created_at,
            updated_at=db_template.updated_at
        )

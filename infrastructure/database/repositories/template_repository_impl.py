from typing import Optional, List
from domain.models.document_template import DocumentTemplate
from domain.repositories.template_repository import TemplateRepository
from infrastructure.database.models import DocumentTemplateModel
from sqlalchemy import select

class TemplateRepositoryImpl(TemplateRepository):
    def __init__(self, database):
        self.database = database
    
    async def get_by_id(self, template_id: str) -> Optional[DocumentTemplate]:
        async with self.database.async_session() as session:
            result = await session.get(DocumentTemplateModel, template_id)
            if result:
                return self._to_entity(result)
            return None
    
    async def get_all_active(self) -> List[DocumentTemplate]:
        async with self.database.async_session() as session:
            stmt = select(DocumentTemplateModel).where(DocumentTemplateModel.is_active == True)
            result = await session.execute(stmt)
            templates = result.scalars().all()
            return [self._to_entity(template) for template in templates]
    
    async def get_by_type(self, doc_type: str) -> List[DocumentTemplate]:
        async with self.database.async_session() as session:
            stmt = select(DocumentTemplateModel).where(
                DocumentTemplateModel.document_type == doc_type,
                DocumentTemplateModel.is_active == True
            )
            result = await session.execute(stmt)
            templates = result.scalars().all()
            return [self._to_entity(template) for template in templates]
    
    async def get_by_category(self, category: str) -> List[DocumentTemplate]:
        async with self.database.async_session() as session:
            stmt = select(DocumentTemplateModel).where(
                DocumentTemplateModel.category == category,
                DocumentTemplateModel.is_active == True
            )
            result = await session.execute(stmt)
            templates = result.scalars().all()
            return [self._to_entity(template) for template in templates]
    
    async def create(self, template: DocumentTemplate) -> DocumentTemplate:
        async with self.database.async_session() as session:
            template_model = DocumentTemplateModel(
                id=template.id,
                name=template.name,
                description=template.description,
                content=template.content,
                document_type=template.document_type,
                variables_schema=template.variables_schema,
                required_variables=template.required_variables,
                category=template.category,
                version=template.version,
                is_active=template.is_active,
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            session.add(template_model)
            await session.commit()
            return template
    
    def _to_entity(self, model: DocumentTemplateModel) -> DocumentTemplate:
        return DocumentTemplate(
            id=model.id,
            name=model.name,
            description=model.description,
            content=model.content,
            document_type=model.document_type,
            variables_schema=model.variables_schema or {},
            required_variables=model.required_variables or [],
            category=model.category,
            version=model.version,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

from typing import Optional
from domain.entities.document import Document, DocumentStatus, DocumentType
from domain.entities.user import User
from domain.repositories.document_repository import DocumentRepository
from domain.repositories.user_repository import UserRepository
from domain.repositories.template_repository import TemplateRepository
from application.dtos.document_dtos import CreateDocumentRequest, DocumentResponse

class CreateDocumentUseCase:
    """Use Case для создания документа"""
    
    def __init__(self, 
                 document_repository: DocumentRepository,
                 user_repository: UserRepository,
                 template_repository: TemplateRepository):
        self._document_repository = document_repository
        self._user_repository = user_repository
        self._template_repository = template_repository
    
    async def execute(self, request: CreateDocumentRequest) -> DocumentResponse:
        # Получаем пользователя
        user = await self._user_repository.get_by_telegram_id(request.user_telegram_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Проверяем лимиты
        if not user.can_create_document():
            raise ValueError("Превышен лимит документов для вашего тарифа")
        
        # Получаем шаблон если указан
        template = None
        if request.template_id:
            template = await self._template_repository.get_by_id(request.template_id)
        
        # Создаем документ
        document = Document(
            title=request.title,
            content=request.content or "",
            document_type=request.document_type,
            status=DocumentStatus.DRAFT,
            user_id=user.id,
            template_id=request.template_id,
            variables=request.variables or {},
            metadata={
                "created_via": "bot",
                "user_telegram_id": request.user_telegram_id
            }
        )
        
        created_document = await self._document_repository.create(document)
        return DocumentResponse.from_domain(created_document)

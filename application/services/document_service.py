from typing import List, Optional
from domain.entities.document import DocumentType
from application.use_cases.documents.create_document import CreateDocumentUseCase
from application.use_cases.documents.get_user_documents import GetUserDocumentsUseCase
from application.dtos.document_dtos import CreateDocumentRequest, DocumentResponse, DocumentListResponse

class DocumentService:
    """Сервис для работы с документами"""
    
    def __init__(self, 
                 create_document_use_case: CreateDocumentUseCase,
                 get_user_documents_use_case: GetUserDocumentsUseCase):
        self._create_document_use_case = create_document_use_case
        self._get_user_documents_use_case = get_user_documents_use_case
    
    async def create_document(self, 
                            user_telegram_id: int,
                            title: str,
                            document_type: DocumentType,
                            content: Optional[str] = None,
                            template_id: Optional[str] = None,
                            variables: Optional[dict] = None) -> DocumentResponse:
        """Создает новый документ"""
        request = CreateDocumentRequest(
            user_telegram_id=user_telegram_id,
            title=title,
            document_type=document_type,
            content=content,
            template_id=template_id,
            variables=variables
        )
        return await self._create_document_use_case.execute(request)
    
    async def get_user_documents(self, user_telegram_id: int) -> DocumentListResponse:
        """Получает документы пользователя"""
        documents = await self._get_user_documents_use_case.execute(user_telegram_id)
        return DocumentListResponse(
            documents=documents,
            total_count=len(documents),
            user_document_limit=10  # Можно вынести в конфигурацию
        )

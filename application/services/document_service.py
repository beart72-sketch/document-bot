from typing import List, Optional
from domain.entities.document import Document, DocumentStatus, DocumentType
from domain.repositories.document_repository import DocumentRepository
from domain.repositories.user_repository import UserRepository

class DocumentService:
    def __init__(self, document_repo: DocumentRepository, user_repo: UserRepository):
        self.document_repo = document_repo
        self.user_repo = user_repo
    
    async def create_document(self, user_telegram_id: int, title: str, 
                            document_type: DocumentType, content: str = "") -> Document:
        """Создает новый документ"""
        # Получаем пользователя
        user = await self.user_repo.get_by_telegram_id(user_telegram_id)
        if not user:
            raise ValueError(f"Пользователь с telegram_id {user_telegram_id} не найден")
        
        # Создаем документ
        document = Document(
            title=title,
            content=content,
            document_type=document_type,
            user_id=user.id,
            status=DocumentStatus.DRAFT
        )
        
        return await self.document_repo.create(document)
    
    async def get_user_documents(self, user_telegram_id: int):
        """Получает документы пользователя"""
        user = await self.user_repo.get_by_telegram_id(user_telegram_id)
        if not user:
            return GetUserDocumentsResponse(documents=[], total_count=0, user_document_limit=10)
        
        documents = await self.document_repo.get_by_user_id(user.id)
        
        return GetUserDocumentsResponse(
            documents=documents,
            total_count=len(documents),
            user_document_limit=10  # TODO: брать из подписки
        )

class GetUserDocumentsResponse:
    def __init__(self, documents: List[Document], total_count: int, user_document_limit: int):
        self.documents = documents
        self.total_count = total_count
        self.user_document_limit = user_document_limit

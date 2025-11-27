from typing import List
from domain.repositories.document_repository import DocumentRepository
from domain.repositories.user_repository import UserRepository
from application.dtos.document_dtos import DocumentResponse

class GetUserDocumentsUseCase:
    """Use Case для получения документов пользователя"""
    
    def __init__(self, 
                 document_repository: DocumentRepository,
                 user_repository: UserRepository):
        self._document_repository = document_repository
        self._user_repository = user_repository
    
    async def execute(self, user_telegram_id: int) -> List[DocumentResponse]:
        # Получаем пользователя
        user = await self._user_repository.get_by_telegram_id(user_telegram_id)
        if not user:
            return []
        
        # Получаем документы пользователя
        documents = await self._document_repository.get_by_user_id(user.id)
        return [DocumentResponse.from_domain(doc) for doc in documents]

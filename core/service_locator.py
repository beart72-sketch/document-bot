from infrastructure.database.database import Database
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from infrastructure.database.repositories.template_repository_impl import TemplateRepositoryImpl
from application.use_cases.users.get_or_create_user import GetOrCreateUserUseCase
from application.use_cases.documents.create_document import CreateDocumentUseCase
from application.use_cases.documents.get_user_documents import GetUserDocumentsUseCase
from application.services.user_service import UserService
from application.services.document_service import DocumentService

class ServiceLocator:
    """Локатор сервисов для правильного доступа к зависимостям"""
    
    def __init__(self):
        self._database = Database()
        self._user_service = None
        self._document_service = None
    
    async def get_user_service(self):
        """Возвращает сервис пользователей"""
        if self._user_service is None:
            session = await self._database.get_session()
            user_repository = UserRepositoryImpl(session)
            self._user_service = UserService(user_repository)
        return self._user_service
    
    async def get_document_service(self):
        """Возвращает сервис документов"""
        if self._document_service is None:
            session = await self._database.get_session()
            
            user_repository = UserRepositoryImpl(session)
            document_repository = DocumentRepositoryImpl(session)
            template_repository = TemplateRepositoryImpl(session)
            
            create_document_use_case = CreateDocumentUseCase(
                document_repository, user_repository, template_repository
            )
            get_user_documents_use_case = GetUserDocumentsUseCase(
                document_repository, user_repository
            )
            
            self._document_service = DocumentService(
                create_document_use_case=create_document_use_case,
                get_user_documents_use_case=get_user_documents_use_case
            )
        return self._document_service
    
    async def get_database(self):
        """Возвращает базу данных"""
        return self._database

# Глобальный экземпляр локатора
service_locator = ServiceLocator()

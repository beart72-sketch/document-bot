from infrastructure.database.database import Database
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from infrastructure.database.repositories.template_repository_impl import TemplateRepositoryImpl
from application.services.user_service import UserService
from application.services.document_service import DocumentService
from domain.services.menu_service import MenuService
from presentation.telegram.keyboards.main_keyboards import MainKeyboards

class ServiceLocator:
    def __init__(self):
        self._database = None
        self._user_service = None
        self._document_service = None
        self._menu_service = None
        self._keyboards = None
    
    async def initialize(self):
        """Инициализация всех сервисов"""
        # Инициализация базы данных
        self._database = Database()
        await self._database.initialize()
        
        # Инициализация репозиториев
        user_repo = UserRepositoryImpl(self._database)
        document_repo = DocumentRepositoryImpl(self._database)
        template_repo = TemplateRepositoryImpl(self._database)
        
        # Инициализация сервисов
        self._user_service = UserService(user_repo)
        self._document_service = DocumentService(document_repo, user_repo)
        self._menu_service = MenuService()
        self._keyboards = MainKeyboards()
    
    async def get_user_service(self) -> UserService:
        if self._user_service is None:
            await self.initialize()
        return self._user_service
    
    async def get_document_service(self) -> DocumentService:
        if self._document_service is None:
            await self.initialize()
        return self._document_service
    
    async def get_menu_service(self) -> MenuService:
        if self._menu_service is None:
            await self.initialize()
        return self._menu_service
    
    def get_keyboards(self) -> MainKeyboards:
        if self._keyboards is None:
            self._keyboards = MainKeyboards()
        return self._keyboards
    
    async def close(self):
        """Закрытие соединений"""
        if self._database:
            await self._database.close()

# Глобальный экземпляр сервис локатора
service_locator = ServiceLocator()

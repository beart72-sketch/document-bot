from dependency_injector import containers, providers
from infrastructure.database.database import Database
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from domain.repositories.user_repository import UserRepository
from application.use_cases.users.get_or_create_user import GetOrCreateUserUseCase
from application.services.user_service import UserService

class Container(containers.DeclarativeContainer):
    """Профессиональный контейнер зависимостей"""
    
    # База данных
    database = providers.Singleton(Database)
    
    # Репозитории
    user_repository = providers.Factory(
        UserRepositoryImpl,
        session=providers.Callable(lambda: database().get_session())
    )
    
    # Use Cases
    get_or_create_user_use_case = providers.Factory(
        GetOrCreateUserUseCase,
        user_repository=user_repository
    )
    
    # Сервисы
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )

# Глобальный экземпляр контейнера
container = Container()

import asyncio
import logging
from uuid import uuid4
from datetime import datetime
from infrastructure.database.database import Database
from infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from application.services.subscription_service import SubscriptionService
from application.services.document_service import DocumentService
from domain.entities.user import User

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_enhanced():
    """Демонстрация расширенной функциональности"""
    
    # Инициализация базы данных
    database = Database()
    await database.connect()
    
    # Инициализация репозиториев
    document_repo = DocumentRepositoryImpl(database)
    user_repo = UserRepositoryImpl(database)
    subscription_repo = SubscriptionRepositoryImpl(database)
    
    # Инициализация сервисов
    subscription_service = SubscriptionService(subscription_repo, user_repo)
    document_service = DocumentService(document_repo, subscription_service)
    
    # Создаем тестового пользователя
    test_user_id = "demo_user_001"
    test_user = User(
        id=test_user_id,
        email="demo@example.com",
        first_name="Демо",
        last_name="Пользователь"
    )
    
    try:
        await user_repo.create(test_user)
        logger.info("✅ Тестовый пользователь создан")
    except Exception as e:
        logger.info("👤 Пользователь уже существует")
    
    logger.info("🚀 ДЕМОНСТРАЦИЯ РАБОТЫ СИСТЕМЫ")
    logger.info("=" * 50)
    
    # 1. Информация о подписке
    subscription_info = await subscription_service.get_subscription_info(test_user_id)
    logger.info("📊 ИНФОРМАЦИЯ О ПОДПИСКЕ:")
    logger.info(f"   • План: {subscription_info['plan']}")
    logger.info(f"   • Статус: {subscription_info['status']}")
    logger.info(f"   • Активна: {subscription_info['is_active']}")
    logger.info(f"   • Дней осталось: {subscription_info['days_remaining']}")
    logger.info(f"   • Лимит документов: {subscription_info['features']['documents_per_month']}")
    
    # 2. Создание документов
    logger.info("\n📝 СОЗДАНИЕ ДОКУМЕНТОВ:")
    
    documents_to_create = [
        {
            "title": "Исковое заявление о защите прав потребителя",
            "content": "В Ленинский районный суд г. Москвы...",
            "type": "claim"
        },
        {
            "title": "Договор аренды квартиры",
            "content": "г. Москва, 27 ноября 2025 г....",
            "type": "contract"
        },
        {
            "title": "Жалоба на действия сотрудника ГИБДД",
            "content": "В прокуратуру г. Москвы...",
            "type": "complaint"
        }
    ]
    
    created_docs = []
    for i, doc_data in enumerate(documents_to_create):
        try:
            document = await document_service.create_document(
                user_id=test_user_id,
                title=doc_data["title"],
                content=doc_data["content"],
                document_type=doc_data["type"]
            )
            created_docs.append(document)
            logger.info(f"   ✅ Документ '{doc_data['title']}' создан")
        except Exception as e:
            logger.error(f"   ❌ Ошибка создания документа: {e}")
    
    # 3. Статистика документов
    logger.info("\n📈 СТАТИСТИКА ДОКУМЕНТОВ:")
    stats = await document_service.get_document_stats(test_user_id)
    logger.info(f"   • Всего документов: {stats['total_documents']}")
    logger.info(f"   • Документов за текущий месяц: {stats['current_month_documents']}")
    logger.info(f"   • Осталось документов: {stats['remaining_documents']}")
    logger.info(f"   • Распределение по типам: {stats['type_distribution']}")
    
    # 4. Проверка лимитов
    logger.info("\n🔍 ПРОВЕРКА ЛИМИТОВ:")
    can_create_more = await subscription_service.check_document_limit(test_user_id, stats['current_month_documents'])
    logger.info(f"   • Можно создать еще документы: {can_create_more}")
    
    remaining_ai = await subscription_service.can_use_ai(test_user_id, 0)
    logger.info(f"   • Можно использовать AI: {remaining_ai}")
    
    # 5. Обновление статуса документа
    if created_docs:
        logger.info("\n🔄 ОБНОВЛЕНИЕ СТАТУСА ДОКУМЕНТА:")
        updated_doc = await document_service.update_document_status(created_docs[0].id, "completed")
        if updated_doc:
            logger.info(f"   ✅ Статус документа обновлен на: {updated_doc.status}")
    
    # 6. Получение всех документов пользователя
    logger.info("\n📋 ВСЕ ДОКУМЕНТЫ ПОЛЬЗОВАТЕЛЯ:")
    user_documents = await document_service.get_user_documents(test_user_id)
    for doc in user_documents:
        logger.info(f"   • {doc.title} ({doc.document_type}) - {doc.status}")
    
    logger.info("\n🎯 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(demo_enhanced())

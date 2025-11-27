import asyncio
import logging
from infrastructure.database.database import Database
from infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from application.services.subscription_service import SubscriptionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_limits():
    """Тестирование лимитов подписки"""
    
    database = Database()
    await database.connect()
    
    document_repo = DocumentRepositoryImpl(database)
    user_repo = UserRepositoryImpl(database)
    subscription_repo = SubscriptionRepositoryImpl(database)
    subscription_service = SubscriptionService(subscription_repo, user_repo)
    
    test_user_id = "limit_test_user"
    
    logger.info("🧪 ТЕСТИРОВАНИЕ ЛИМИТОВ ПОДПИСКИ")
    logger.info("=" * 40)
    
    # Тестируем различные сценарии
    test_scenarios = [
        ("Создание 3 документов при лимите 5", 3, True),
        ("Создание 5 документов при лимите 5", 5, False),
        ("Создание 6 документов при лимите 5", 6, False),
        ("Создание 0 документов при лимите 5", 0, True),
    ]
    
    for description, doc_count, expected in test_scenarios:
        result = await subscription_service.check_document_limit(test_user_id, doc_count)
        status = "✅ ПРОЙДЕН" if result == expected else "❌ НЕ ПРОЙДЕН"
        logger.info(f"{status} {description}: результат={result}, ожидалось={expected}")
    
    # Тестируем AI лимиты
    logger.info("\n🤖 ТЕСТИРОВАНИЕ AI ЛИМИТОВ:")
    ai_test_scenarios = [
        ("0 AI запросов при лимите 10", 0, True),
        ("5 AI запросов при лимите 10", 5, True),
        ("10 AI запросов при лимите 10", 10, False),
        ("15 AI запросов при лимите 10", 15, False),
    ]
    
    for description, ai_count, expected in ai_test_scenarios:
        result = await subscription_service.can_use_ai(test_user_id, ai_count)
        status = "✅ ПРОЙДЕН" if result == expected else "❌ НЕ ПРОЙДЕН"
        logger.info(f"{status} {description}: результат={result}, ожидалось={expected}")
    
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(test_limits())

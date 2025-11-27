import asyncio
import logging
from telebot.async_telebot import AsyncTeleBot
from core.config import config
from infrastructure.database.database import Database
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from infrastructure.database.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from application.services.user_service import UserService
from application.services.document_service import DocumentService
from application.services.subscription_service import SubscriptionService
from domain.services.menu_service import MenuService
from presentation.telegram.keyboards.main_keyboards import MainKeyboards
from presentation.telegram.facades.bot_facade import BotFacade

logger = logging.getLogger(__name__)

async def run_bot():
    """Запуск Telegram бота с правильной инициализацией сервисов"""
    
    # Инициализация базы данных
    db = Database()
    await db.initialize()
    logger.info("✅ База данных инициализирована")
    
    # Создание репозиториев
    user_repo = UserRepositoryImpl(db)
    document_repo = DocumentRepositoryImpl(db)
    subscription_repo = SubscriptionRepositoryImpl(db)
    logger.info("✅ Репозитории созданы")
    
    # Создание сервисов
    subscription_service = SubscriptionService(subscription_repo, user_repo)
    user_service = UserService(user_repo, subscription_service)
    document_service = DocumentService(
        document_repo, 
        user_repo, 
        subscription_service
    )
    menu_service = MenuService()
    keyboards = MainKeyboards(menu_service)  # 🔥 ИСПРАВЛЕНО: передаем menu_service
    logger.info("✅ Сервисы созданы")
    
    # Создание бота
    bot = AsyncTeleBot(config.TOKEN)
    logger.info("✅ Telegram бот создан")
    
    # Создание фасада
    bot_facade = BotFacade(
        bot=bot,
        user_service=user_service,
        document_service=document_service,
        subscription_service=subscription_service,
        menu_service=menu_service,
        keyboards=keyboards
    )
    logger.info("✅ Фасад бота создан")
    
    # Регистрация обработчиков
    @bot.message_handler(commands=['start'])
    async def start_command(message):
        await bot_facade.handle_start(message)
    
    @bot.message_handler(func=lambda message: True)
    async def handle_all_messages(message):
        await bot_facade.handle_message(message)
    
    logger.info("✅ Обработчики зарегистрированы")
    logger.info(f"🤖 Бот запущен. Токен: {'*' * 10 if config.TOKEN else 'NOT SET'}")
    
    # Запуск polling
    try:
        await bot.polling(non_stop=True)
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        raise
    finally:
        await db.close()
        logger.info("🔒 База данных закрыта")

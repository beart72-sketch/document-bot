import asyncio
import logging
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiException
from core.config import config
from core.service_locator import service_locator
from presentation.telegram.facades.bot_facade import BotFacade

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = AsyncTeleBot(config.telegram.bot_token)
        self.user_service = None
        self.document_service = None
        self.subscription_service = None
        self.menu_service = None
        self.keyboards = None
        self.bot_facade = None
    
    async def initialize_services(self):
        """Инициализация сервисов"""
        self.user_service = await service_locator.get_user_service()
        self.document_service = await service_locator.get_document_service()
        self.subscription_service = await service_locator.get_subscription_service()
        self.menu_service = await service_locator.get_menu_service()
        self.keyboards = service_locator.get_keyboards()
        
        self.bot_facade = BotFacade(
            bot=self.bot,
            user_service=self.user_service,
            document_service=self.document_service,
            subscription_service=self.subscription_service,
            menu_service=self.menu_service,
            keyboards=self.keyboards
        )
    
    async def _initialize(self):
        """Инициализация бота"""
        await self.initialize_services()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков"""
        # Команды
        self.bot.message_handler(commands=['start'])(self.bot_facade.handle_start)
        self.bot.message_handler(commands=['help'])(self.bot_facade.handle_help)
        self.bot.message_handler(commands=['payment'])(self.bot_facade.handle_payment)
        
        # Текстовые сообщения
        self.bot.message_handler(func=lambda message: True)(self.bot_facade.handle_message)
    
    async def run(self):
        """Запуск бота"""
        try:
            await self._initialize()
            logger.info("🤖 Бот запускается...")
            await self.bot.infinity_polling()
        except Exception as e:
            await self._handle_error(e)
    
    async def _handle_error(self, error: Exception):
        """Обработка ошибок"""
        logger.error(f"❌ Критическая ошибка при запуске бота: {error}")
        raise error

async def run_bot():
    """Основная функция запуска бота"""
    try:
        # Инициализируем сервис локатор
        await service_locator.initialize()
        
        # Создаем и запускаем бота
        bot = TelegramBot()
        await bot.run()
        
    except ApiException as e:
        if "Forbidden" in str(e):
            logger.error("❌ Бот заблокирован пользователем или не активирован")
        else:
            logger.error(f"❌ Ошибка Telegram API: {e}")
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        raise
    finally:
        # Закрываем соединения
        await service_locator.close()

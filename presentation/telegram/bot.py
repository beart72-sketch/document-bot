#!/usr/bin/env python3
"""
Professional Telegram Bot Module
"""
import asyncio
from telebot.async_telebot import AsyncTeleBot
from core.config import load_config
from core.service_locator import service_locator
from domain.services.menu_service import MenuService
from presentation.telegram.keyboards.main_keyboards import MainKeyboards
from presentation.telegram.facades.bot_facade import BotFacade

class TelegramBot:
    """Профессиональная реализация Telegram бота"""
    
    def __init__(self):
        self.config = load_config()
        self.bot = AsyncTeleBot(self.config.bot_token)
        
        # Инициализация сервисов
        self.menu_service = MenuService()
        self.keyboards = MainKeyboards(self.menu_service)
        self.user_service = None
        self.document_service = None
        
        # Фасад для обработки сообщений
        self.facade = None
        
        self._register_handlers()
    
    async def initialize_services(self):
        """Асинхронная инициализация сервисов"""
        self.user_service = await service_locator.get_user_service()
        self.document_service = await service_locator.get_document_service()
        self.facade = BotFacade(
            bot=self.bot,
            user_service=self.user_service,
            document_service=self.document_service,
            menu_service=self.menu_service,
            keyboards=self.keyboards
        )
    
    def _register_handlers(self):
        """Регистрация обработчиков сообщений"""
        
        @self.bot.message_handler(commands=['start'])
        async def handle_start(message):
            await self.facade.handle_start(message)
        
        @self.bot.message_handler(func=lambda message: True)
        async def handle_all_messages(message):
            await self.facade.handle_message(message)
    
    async def run(self):
        """Запуск бота"""
        try:
            await self._initialize()
            await self._start_polling()
            
        except Exception as e:
            await self._handle_error(e)
    
    async def _initialize(self):
        """Инициализация приложения"""
        database = await service_locator.get_database()
        
        print(f"🔑 Токен: {self.config.bot_token[:10]}...")
        print(f"🤖 Бот: @Sud_keis_bot")
        print(f"🔗 Ссылка: https://t.me/Sud_keis_bot")
        
        # Проверка подключения к базе данных
        if await database.health_check():
            print("✅ Подключение к базе данных установлено")
        else:
            raise Exception("❌ Ошибка подключения к базе данных")
        
        # Создание таблиц
        await database.create_tables()
        print("✅ Таблицы базы данных проверены/созданы")
        
        # Инициализация сервисов
        await self.initialize_services()
        print("✅ Сервисы инициализированы")
        
        print("🤖 Бот запускается...")
        print("📱 Откройте Telegram и напишите боту @Sud_keis_bot")
    
    async def _start_polling(self):
        """Запуск опроса Telegram API"""
        await self.bot.polling(non_stop=True)
    
    async def _handle_error(self, error: Exception):
        """Обработка ошибок"""
        print(f"❌ Критическая ошибка при запуске бота: {error}")
        import traceback
        traceback.print_exc()
        raise error

async def run_bot():
    """Точка входа для запуска бота"""
    bot = TelegramBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(run_bot())

"""
Скрипт для обновления бота с новой конфигурацией
"""

import os
import sys
from config import Config

def update_bot_files():
    """Обновляем файлы бота для использования новой конфигурации"""
    
    # Обновляем main.py бота
    bot_main_content = '''import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from infrastructure.database.database import Database
from infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.subscription_repository_impl import SubscriptionRepositoryImpl
from application.services.subscription_service import SubscriptionService
from application.services.document_service import DocumentService
from domain.entities.user import User
from config import Config

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Config.LOGS_DIR, 'bot.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Проверка конфигурации
config_errors = Config.validate()
if config_errors:
    for error in config_errors:
        logger.error(f"❌ Ошибка конфигурации: {error}")
    sys.exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=Config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация базы данных и сервисов
database = Database()
document_repo = None
user_repo = None
subscription_repo = None
subscription_service = None
document_service = None

# Состояния FSM
class DocumentCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_type = State()

class UserRegistration(StatesGroup):
    waiting_for_email = State()

# Клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои документы"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="💳 Подписка"), KeyboardButton(text="📝 Создать документ")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )

def get_document_types_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Исковое заявление", callback_data="type_claim")],
            [InlineKeyboardButton(text="📑 Договор", callback_data="type_contract")],
            [InlineKeyboardButton(text="📝 Жалоба", callback_data="type_complaint")],
            [InlineKeyboardButton(text="⚖️ Ходатайство", callback_data="type_motion")]
        ]
    )

def get_subscription_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💎 Премиум (50 документов/мес)", callback_data="upgrade_premium")],
            [InlineKeyboardButton(text="🏢 Бизнес (500 документов/мес)", callback_data="upgrade_business")],
            [InlineKeyboardButton(text="📊 Сравнить тарифы", callback_data="compare_plans")]
        ]
    )

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Статистика пользователей")],
            [KeyboardButton(text="📊 Общая статистика")],
            [KeyboardButton(text="💾 Создать бэкап")],
            [KeyboardButton(text="📋 Главное меню")]
        ],
        resize_keyboard=True
    )

# Проверка прав администратора
def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMIN_IDS

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Проверка администратора
    if is_admin(user_id):
        await message.answer("👑 Добро пожаловать, администратор!", reply_markup=get_admin_keyboard())
        return
    
    # Регистрация обычного пользователя
    user_id_str = str(user_id)
    user = User(
        id=user_id_str,
        email=f"user_{user_id}@telegram.org",
        first_name=user_name,
        last_name=message.from_user.last_name or ""
    )
    
    try:
        existing_user = await user_repo.get_by_id(user_id_str)
        if not existing_user:
            await user_repo.create(user)
            await subscription_service.create_free_subscription(user_id_str)
            logger.info(f"✅ Новый пользователь зарегистрирован: {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка регистрации пользователя: {e}")
    
    welcome_text = f"""
👋 Привет, {user_name}!

🤖 Я - бот для создания юридических документов. 
С моей помощью вы можете быстро создавать:

• 📄 Исковые заявления
• 📑 Договоры  
• 📝 Жалобы
• ⚖️ Ходатайства

🎯 Выберите действие в меню ниже:
    """
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Панель администратора"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав доступа к панели администратора")
        return
    
    stats_text = """
👑 Панель администратора

Доступные действия:
• 👥 Статистика пользователей
• 📊 Общая статистика
• 💾 Создать бэкап базы данных
    """
    
    await message.answer(stats_text, reply_markup=get_admin_keyboard())

@dp.message(lambda message: message.text == "👥 Статистика пользователей" and is_admin(message.from_user.id))
async def admin_user_stats(message: Message):
    """Статистика пользователей для администратора"""
    try:
        users = await user_repo.get_all()
        subscriptions = await subscription_repo.get_all()
        
        active_users = len([u for u in users if u.is_active])
        total_documents = len(await document_repo.get_all())
        
        plan_stats = {}
        for sub in subscriptions:
            plan_stats[sub.plan] = plan_stats.get(sub.plan, 0) + 1
        
        response = f"""
👥 Статистика пользователей

📊 Общая статистика:
• Всего пользователей: {len(users)}
• Активных пользователей: {active_users}
• Всего документов: {total_documents}

💳 Распределение по подпискам:
"""
        for plan, count in plan_stats.items():
            response += f"• {plan.upper()}: {count} пользователей\\n"
        
        response += f"\\n📈 Последние 5 пользователей:\\n"
        for user in users[-5:]:
            response += f"• {user.first_name} ({user.email}) - {user.created_at.strftime('%d.%m.%Y') if user.created_at else 'N/A'}\\n"
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики пользователей: {e}")
        await message.answer("❌ Ошибка при получении статистики")

# ... остальные обработчики из предыдущей версии ...

async def main():
    """Основная функция запуска бота"""
    global document_repo, user_repo, subscription_repo, subscription_service, document_service
    
    logger.info("🤖 Запуск Legal Documents Bot с новой конфигурацией...")
    
    # Инициализация базы данных
    await database.connect(Config.DB_URL)
    
    # Инициализация репозиториев
    document_repo = DocumentRepositoryImpl(database)
    user_repo = UserRepositoryImpl(database)
    subscription_repo = SubscriptionRepositoryImpl(database)
    
    # Инициализация сервисов
    subscription_service = SubscriptionService(subscription_repo, user_repo)
    document_service = DocumentService(document_repo, subscription_service)
    
    logger.info("✅ Бот инициализирован и готов к работе")
    logger.info(f"👑 Администраторы: {Config.ADMIN_IDS}")
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

    # Записываем обновленный main.py
    with open('bot/main.py', 'w', encoding='utf-8') as f:
        f.write(bot_main_content)
    
    print("✅ Файлы бота обновлены для использования новой конфигурации")

if __name__ == "__main__":
    update_bot_files()
    print("🎉 Конфигурация обновлена!")
    print("📝 Не забудьте:")
    print("   1. Заменить токен в .env файле")
    print("   2. Указать ваш Telegram ID в ADMIN_IDS")
    print("   3. Запустить бота: python run_bot.py")

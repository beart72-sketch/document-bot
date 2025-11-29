import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Добавляем пути для импорта родительских модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from domain.models.user import User
from core.config import Config

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

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    # Регистрация пользователя в системе
    user = User(
        id=user_id,
        email=f"user_{user_id}@telegram.org",
        first_name=user_name,
        last_name=message.from_user.last_name or ""
    )
    
    try:
        existing_user = await user_repo.get_by_id(user_id)
        if not existing_user:
            await user_repo.create(user)
            await subscription_service.create_free_subscription(user_id)
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

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📖 **Помощь по боту:**

**Основные команды:**
/start - Начать работу
/help - Получить помощь

**Функционал:**
📋 Мои документы - Просмотр всех документов
📊 Статистика - Аналитика по документам
💳 Подписка - Управление подпиской
📝 Создать документ - Создание нового документа

Для начала работы нажмите /start
    """
    await message.answer(help_text, reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text == "📋 Мои документы")
async def show_documents(message: Message):
    user_id = str(message.from_user.id)
    
    try:
        documents = await document_service.get_user_documents(user_id)
        
        if not documents:
            await message.answer("📭 У вас пока нет документов.\n\nСоздайте первый документ через меню \"📝 Создать документ\"")
            return
        
        response = f"📋 **Ваши документы** ({len(documents)}):\n\n"
        
        for i, doc in enumerate(documents, 1):
            status_emoji = {
                "draft": "📝",
                "in_progress": "🔄", 
                "completed": "✅",
                "archived": "📁"
            }.get(doc.status, "📄")
            
            type_emoji = {
                "claim": "📄",
                "contract": "📑",
                "complaint": "📝", 
                "motion": "⚖️"
            }.get(doc.document_type, "📄")
            
            response += f"{i}. {status_emoji} {type_emoji} **{doc.title}**\n"
            response += f"   🏷 Тип: {doc.document_type}\n"
            response += f"   📊 Статус: {doc.status}\n"
            response += f"   📅 Создан: {doc.created_at.strftime('%d.%m.%Y') if doc.created_at else 'N/A'}\n\n"
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения документов: {e}")
        await message.answer("❌ Произошла ошибка при загрузке документов")

@dp.message(lambda message: message.text == "📊 Статистика")
async def show_stats(message: Message):
    user_id = str(message.from_user.id)
    
    try:
        stats = await document_service.get_document_stats(user_id)
        subscription_info = await subscription_service.get_subscription_info(user_id)
        
        response = f"""
📈 **Статистика документов**

📋 Всего документов: {stats['total_documents']}
📅 Документов в этом месяце: {stats['current_month_documents']}
🎯 Осталось документов: {stats['remaining_documents']}

💳 **Подписка:**
• План: {subscription_info['plan'].upper()}
• Статус: {'✅ Активна' if subscription_info['is_active'] else '❌ Неактивна'}
• Дней осталось: {subscription_info['days_remaining']}

📊 **Распределение по типам:**
"""
        
        for doc_type, count in stats['type_distribution'].items():
            type_name = {
                "claim": "Исковые заявления",
                "contract": "Договоры",
                "complaint": "Жалобы",
                "motion": "Ходатайства"
            }.get(doc_type, doc_type)
            
            response += f"• {type_name}: {count}\n"
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        await message.answer("❌ Произошла ошибка при загрузке статистики")

@dp.message(lambda message: message.text == "💳 Подписка")
async def show_subscription(message: Message):
    user_id = str(message.from_user.id)
    
    try:
        subscription_info = await subscription_service.get_subscription_info(user_id)
        features = subscription_info['features']
        
        response = f"""
💳 **Информация о подписке**

📋 План: **{subscription_info['plan'].upper()}**
📊 Статус: **{'✅ Активна' if subscription_info['is_active'] else '❌ Неактивна'}**
⏰ Дней осталось: **{subscription_info['days_remaining']}**

🎯 **Лимиты вашего плана:**
• 📄 Документов в месяц: {features['documents_per_month']}
• 🤖 AI запросов: {features['ai_requests']}
• 📝 Макс. длина документа: {features['max_document_length']} символов
• 🎯 Доступные шаблоны: {', '.join(features['templates_access'])}

💎 Для увеличения лимитов обратитесь к администратору.
        """
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о подписке: {e}")
        await message.answer("❌ Произошла ошибка при загрузке информации о подписке")

@dp.message(lambda message: message.text == "📝 Создать документ")
async def start_document_creation(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    
    # Проверяем лимиты
    try:
        documents = await document_service.get_user_documents(user_id)
        current_month_docs = document_service._count_current_month_documents(documents)
        
        can_create = await subscription_service.check_document_limit(user_id, current_month_docs)
        if not can_create:
            remaining = await subscription_service.get_remaining_documents(user_id, current_month_docs)
            await message.answer(f"""
❌ **Лимит документов исчерпан**

Вы создали {current_month_docs} документов в этом месяце.
Доступно документов: {remaining}

💳 Обновите подписку, чтобы создавать больше документов!
            """)
            return
    except Exception as e:
        logger.error(f"❌ Ошибка проверки лимитов: {e}")
    
    await state.set_state(DocumentCreation.waiting_for_type)
    await message.answer("📝 Выберите тип документа:", reply_markup=get_document_types_keyboard())

@dp.callback_query(lambda c: c.data.startswith('type_'))
async def process_document_type(callback: types.CallbackQuery, state: FSMContext):
    doc_type = callback.data.replace('type_', '')
    
    type_names = {
        "claim": "📄 Исковое заявление",
        "contract": "📑 Договор", 
        "complaint": "📝 Жалоба",
        "motion": "⚖️ Ходатайство"
    }
    
    await state.update_data(document_type=doc_type)
    await state.set_state(DocumentCreation.waiting_for_title)
    
    await callback.message.edit_text(f"""
🎯 Выбран тип: **{type_names.get(doc_type, doc_type)}**

📌 Теперь введите **название** для вашего документа.

*Пример: "Исковое заявление о защите прав потребителя"*
    """)
    await callback.answer()

@dp.message(DocumentCreation.waiting_for_title)
async def process_document_title(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Создание документа отменено", reply_markup=get_main_keyboard())
        return
        
    await state.update_data(title=message.text)
    await state.set_state(DocumentCreation.waiting_for_content)
    
    await message.answer("""
📝 Теперь введите **содержание** документа.

*Вы можете ввести текст документа или его основную часть.*
    """, reply_markup=get_cancel_keyboard())

@dp.message(DocumentCreation.waiting_for_content)
async def process_document_content(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Создание документа отменено", reply_markup=get_main_keyboard())
        return
        
    user_id = str(message.from_user.id)
    content = message.text
    
    try:
        data = await state.get_data()
        
        # Создаем документ
        document = await document_service.create_document(
            user_id=user_id,
            title=data['title'],
            content=content,
            document_type=data['document_type']
        )
        
        type_names = {
            "claim": "📄 Исковое заявление",
            "contract": "📑 Договор",
            "complaint": "📝 Жалоба", 
            "motion": "⚖️ Ходатайство"
        }
        
        await message.answer(f"""
✅ **Документ успешно создан!**

📌 **Название:** {document.title}
🏷 **Тип:** {type_names.get(document.document_type, document.document_type)}
📊 **Статус:** Черновик
🆔 **ID:** {document.id[:8]}...

💡 Вы можете просмотреть все свои документы через меню "📋 Мои документы"
        """, reply_markup=get_main_keyboard())
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания документа: {e}")
        await message.answer("""
❌ **Произошла ошибка при создании документа**

Возможные причины:
• Превышен лимит документов для вашей подписки
• Технические неполадки

Попробуйте позже или проверьте вашу подписку.
        """, reply_markup=get_main_keyboard())
        await state.clear()

@dp.message()
async def handle_other_messages(message: Message):
    await message.answer("""
🤖 Я не понял ваше сообщение.

Используйте кнопки меню или команды:
/start - Главное меню
/help - Помощь
    """, reply_markup=get_main_keyboard())

async def main():
    """Основная функция запуска бота"""
    global document_repo, user_repo, subscription_repo, subscription_service, document_service
    
    # Проверка конфигурации
    config_errors = Config.validate()
    if config_errors:
        for error in config_errors:
            logger.error(f"❌ Ошибка конфигурации: {error}")
        return
    
    # Инициализация базы данных
    await database.connect(Config.DB_URL)
    
    # Инициализация репозиториев
    document_repo = DocumentRepositoryImpl(database)
    user_repo = UserRepositoryImpl(database)
    subscription_repo = SubscriptionRepositoryImpl(database)
    
    # Инициализация сервисов
    subscription_service = SubscriptionService(subscription_repo, user_repo)
    document_service = DocumentService(document_repo, subscription_service)
    
    logger.info("🤖 Бот инициализирован и готов к работе")
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from presentation.telegram.keyboards import (
    get_main_keyboard,
    get_document_types_keyboard,
    get_subscription_keyboard,
    get_subscription_plans_keyboard,
    get_back_keyboard
)

logger = logging.getLogger(__name__)
main_router = Router()

# ===== КОМАНДЫ =====
@main_router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    logger.info(f"🎯 /start от {message.from_user.id}")
    
    welcome_text = (
        "👋 *Добро пожаловать в бот для создания документов!*\n\n"
        "🚀 *Используйте кнопки ПОД этим сообщением* для навигации\n\n"
        "📄 *Создать документ* - выбор типа документа\n"
        "📁 *Мои документы* - просмотр ваших документов\n"
        "💳 *Подписка* - управление подпиской\n"
        "ℹ️ *Помощь* - справка по использованию"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@main_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await show_detailed_help(message)

@main_router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Команда для принудительного показа меню"""
    logger.info(f"🎯 /menu от {message.from_user.id}")
    text = "🏠 *Главное меню*\n\nВыберите действие:"
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ===== ДЕТАЛЬНАЯ ПОМОЩЬ =====
async def show_detailed_help(message_or_callback):
    """Показать детальную справку"""
    help_text = (
        "ℹ️ *ПОМОЩЬ И ИНСТРУКЦИЯ*\n\n"
        
        "🔸 *ОСНОВНЫЕ ВОЗМОЖНОСТИ:*\n"
        "• 📄 *Создание документов* - юридические шаблоны\n"  
        "• 📁 *Мои документы* - история созданных файлов\n"
        "• 💳 *Подписка* - тарифы и управление\n\n"
        
        "🔸 *КАК СОЗДАТЬ ДОКУМЕНТ:*\n"
        "1. Нажмите '📄 Создать документ'\n"
        "2. Выберите тип документа:\n"
        "   - *Договор* - соглашения между сторонами\n"
        "   - *Акт* - приемка-передача\n"
        "   - *Заявление* - официальные обращения\n"
        "   - *Доверенность* - передача полномочий\n"
        "3. Следуйте инструкциям бота\n"
        "4. Получите готовый документ\n\n"
        
        "🔸 *ТИПЫ ДОКУМЕНТОВ:*\n"
        "• *Договор* - для бизнес-соглашений\n"
        "• *Акт* - для фиксации фактов\n" 
        "• *Заявление* - для официальных обращений\n"
        "• *Доверенность* - для представительства\n\n"
        
        "🔸 *КОМАНДЫ:*\n"
        "*/start* - главное меню\n"
        "*/help* - эта справка\n" 
        "*/menu* - показать меню\n\n"
        
        "🔸 *ПОДДЕРЖКА:*\n"
        "По вопросам работы бота обращайтесь к администратору"
    )
    
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        # Это callback
        await message_or_callback.message.edit_text(help_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
        await message_or_callback.answer()

# ===== CALLBACK ОБРАБОТЧИКИ =====
@main_router.callback_query(F.data == "menu:main")
async def main_menu_handler(callback: CallbackQuery):
    """Главное меню"""
    logger.info(f"🎯 Главное меню от {callback.from_user.id}")
    text = "🏠 *Главное меню*\n\nВыберите действие:"
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data == "menu:create_document")
async def create_document_handler(callback: CallbackQuery):
    """Создание документа"""
    logger.info(f"🎯 Создание документа от {callback.from_user.id}")
    
    text = (
        "📝 *Создание документа*\n\n"
        "Выберите тип документа:\n\n"
        "• *Договор* - для соглашений между сторонами\n"  
        "• *Акт* - для приемки-передачи товаров/услуг\n"
        "• *Заявление* - для официальных обращений\n"
        "• *Доверенность* - для передачи полномочий\n\n"
        "Каждый тип имеет свой шаблон и набор полей"
    )
    
    await callback.message.edit_text(text, reply_markup=get_document_types_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data == "menu:my_documents")
async def my_documents_handler(callback: CallbackQuery):
    """Мои документы"""
    logger.info(f"🎯 Мои документы от {callback.from_user.id}")
    
    text = (
        "📁 *Ваши документы*\n\n"
        "Здесь будут отображаться все созданные вами документы.\n\n"
        "⚡ *Сейчас в разработке:*\n"
        "• История документов\n"
        "• Поиск по документам\n" 
        "• Скачивание файлов\n"
        "• Управление документами\n\n"
        "Создайте свой первый документ! 👆"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data == "menu:subscription")
async def subscription_handler(callback: CallbackQuery):
    """Подписка"""
    logger.info(f"🎯 Подписка от {callback.from_user.id}")
    
    text = (
        "💳 *Управление подпиской*\n\n"
        "Доступные функции:\n\n"
        "• Просмотр текущего тарифа\n"
        "• Статистика использования\n"
        "• Покупка подписки\n"
        "• История платежей\n\n"
        "Выберите действие:"
    )
    
    await callback.message.edit_text(text, reply_markup=get_subscription_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data == "menu:help")
async def help_handler(callback: CallbackQuery):
    """Помощь"""
    logger.info(f"🎯 Помощь от {callback.from_user.id}")
    await show_detailed_help(callback)

@main_router.callback_query(F.data.startswith("subscription:"))
async def subscription_action_handler(callback: CallbackQuery):
    """Действия подписки"""
    action = callback.data.split(":")[1]
    logger.info(f"🎯 Действие подписки '{action}' от {callback.from_user.id}")
    
    if action == "buy":
        text = (
            "💳 *Выберите тариф подписки*\n\n"
            "🟢 *Базовый* - 299₽/мес\n"
            "   • 10 документов в месяц\n"
            "   • Базовые шаблоны\n\n"
            "🔵 *Про* - 599₽/мес\n"
            "   • 50 документов в месяц\n" 
            "   • Расширенные шаблоны\n"
            "   • Приоритетная поддержка\n\n"
            "🟣 *Премиум* - 999₽/мес\n"
            "   • Безлимитное создание\n"
            "   • Все шаблоны\n"
            "   • Персональная поддержка"
        )
        await callback.message.edit_text(text, reply_markup=get_subscription_plans_keyboard(), parse_mode="Markdown")
    elif action == "stats":
        text = (
            "📊 *Ваша статистика*\n\n"
            "• Создано документов: *0*\n"
            "• Доступно документов: *10*\n"
            "• Тариф: *Бесплатный*\n"
            "• Срок подписки: *не активна*\n\n"
            "⚡ *Бесплатный тариф включает:*\n"
            "• 10 документов в месяц\n"
            "• Базовые шаблоны\n"
            "• Стандартная поддержка"
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith("subscription_plan:"))
async def subscription_plan_handler(callback: CallbackQuery):
    """Выбор тарифа"""
    plan = callback.data.split(":")[1]
    plan_names = {
        "basic": "🟢 Базовый (299₽/мес)",
        "pro": "🔵 Про (599₽/мес)", 
        "premium": "🟣 Премиум (999₽/мес)"
    }
    
    plan_details = {
        "basic": "10 документов/мес, базовые шаблоны",
        "pro": "50 документов/мес, расширенные шаблоны", 
        "premium": "Безлимит, все шаблоны, премиум-поддержка"
    }
    
    logger.info(f"🎯 Выбор тарифа '{plan}' от {callback.from_user.id}")
    
    text = (
        f"💳 *Выбран тариф:* {plan_names[plan]}\n\n"
        f"⚡ *Включает:* {plan_details[plan]}\n\n"
        "⚙️ *Функция оплаты находится в разработке*\n\n"
        "Скоро здесь будет интеграция с платежной системой"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="Markdown")
    await callback.answer(f"💳 {plan_names[plan]}")

# ===== УЛУЧШЕННЫЙ FALLBACK ОБРАБОТЧИК =====
@main_router.message()
async def unknown_message_handler(message: Message):
    """Обработчик неизвестных сообщений"""
    user_text = message.text or ""
    logger.info(f"🔴 Неизвестный текст: '{user_text}' от {message.from_user.id}")
    
    # Обработка старых текстовых команд
    command_mapping = {
        '📋 создать документ': 'menu:create_document',
        '📁 мои документы': 'menu:my_documents', 
        '💳 подписка': 'menu:subscription',
        'ℹ️ помощь': 'menu:help'
    }
    
    normalized_text = user_text.lower().strip()
    
    if normalized_text in command_mapping:
        # Если пользователь отправил старую текстовую команду
        callback_data = command_mapping[normalized_text]
        
        # Создаем имитацию callback для обработки
        class MockCallback:
            def __init__(self, message, data):
                self.message = message
                self.data = data
                self.from_user = message.from_user
                self.id = f"mock_{message.message_id}"
        
        mock_callback = MockCallback(message, callback_data)
        
        # Вызываем соответствующий обработчик
        if callback_data == "menu:create_document":
            await create_document_handler(mock_callback)
        elif callback_data == "menu:my_documents":
            await my_documents_handler(mock_callback)
        elif callback_data == "menu:subscription":
            await subscription_handler(mock_callback)
        elif callback_data == "menu:help":
            await help_handler(mock_callback)
            
    elif user_text.lower() in ['start', 'старт', 'меню', 'menu']:
        await cmd_start(message)
    else:
        # Общее сообщение для неизвестных команд
        text = (
            "🔄 *Бот был обновлен!*\n\n"
            "Теперь используйте *инлайн-кнопки* под сообщениями для навигации.\n\n"
            "🚀 *Как пользоваться:*\n"
            "1. Отправьте команду */start*\n"  
            "2. Используйте кнопки *ПОД сообщением*\n"
            "3. Выбирайте нужные действия\n\n"
            "Ваши старые команды теперь работают через кнопки 👇"
        )
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

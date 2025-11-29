from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главная инлайн-клавиатура"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="📄 Создать документ", 
        callback_data="menu:create_document"
    ))
    builder.add(InlineKeyboardButton(
        text="📁 Мои документы", 
        callback_data="menu:my_documents"
    ))
    builder.add(InlineKeyboardButton(
        text="💳 Подписка", 
        callback_data="menu:subscription"
    ))
    builder.add(InlineKeyboardButton(
        text="ℹ️ Помощь", 
        callback_data="menu:help"
    ))
    
    builder.adjust(2)
    return builder.as_markup()


def get_document_types_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа документа"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="📝 Договор", 
        callback_data="document_type:contract"
    ))
    builder.add(InlineKeyboardButton(
        text="📋 Акт", 
        callback_data="document_type:act"
    ))
    builder.add(InlineKeyboardButton(
        text="📄 Заявление", 
        callback_data="document_type:statement"
    ))
    builder.add(InlineKeyboardButton(
        text="🏠 Доверенность", 
        callback_data="document_type:proxy"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад", 
        callback_data="menu:main"
    ))
    
    builder.adjust(2)
    return builder.as_markup()


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подписки"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="💳 Купить подписку", 
        callback_data="subscription:buy"
    ))
    builder.add(InlineKeyboardButton(
        text="📊 Статистика", 
        callback_data="subscription:stats"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад", 
        callback_data="menu:main"
    ))
    
    builder.adjust(1)
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'Назад'"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="🔙 Назад", 
        callback_data="menu:main"
    ))
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'Отмена'"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="❌ Отмена", 
        callback_data="menu:cancel"
    ))
    return builder.as_markup()

"""Клавиатуры для бота"""

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Основная inline-клавиатура (2 кнопки в ряду)"""
    builder = InlineKeyboardBuilder()
    
    # Добавляем все кнопки
    builder.button(text="📝 Создать документ", callback_data="create_document")
    builder.button(text="📋 Мои документы", callback_data="my_documents")
    builder.button(text="📊 Статистика", callback_data="statistics")
    builder.button(text="💳 Подписка", callback_data="subscription")
    builder.button(text="⚙️ Настройки", callback_data="settings")
    builder.button(text="ℹ️ Помощь", callback_data="help")
    
    # ⚠️ КРИТИЧЕСКИ ВАЖНО: adjust() должен быть ПОСЛЕ добавления кнопок
    builder.adjust(2)  # ← именно 2 кнопки в ряду, всегда
    
    return builder.as_markup()

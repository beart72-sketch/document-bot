from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_document_actions_keyboard(document_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с документом"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="📝 Редактировать", 
        callback_data=f"document_edit:{document_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="📄 Скачать", 
        callback_data=f"document_download:{document_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🗑️ Удалить", 
        callback_data=f"document_delete:{document_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад", 
        callback_data="menu:documents"
    ))
    
    builder.adjust(2)
    return builder.as_markup()


def get_documents_list_keyboard(
    documents: list, 
    page: int = 0, 
    has_next: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура для списка документов с пагинацией"""
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки документов
    for doc in documents:
        builder.add(InlineKeyboardButton(
            text=f"📄 {doc.get('title', 'Без названия')}",
            callback_data=f"document_view:{doc['id']}"
        ))
    
    # Добавляем пагинацию
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"documents_page:{page-1}"
        ))
    if has_next:
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"documents_page:{page+1}"
        ))
    
    if pagination_buttons:
        builder.row(*pagination_buttons)
    
    builder.row(InlineKeyboardButton(
        text="🔙 Главное меню",
        callback_data="menu:main"
    ))
    
    return builder.as_markup()

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class MenuType(Enum):
    MAIN = "main"
    DOCUMENT_TYPES = "document_types"
    DOCUMENT_CREATION = "document_creation"

@dataclass
class MenuItem:
    text: str
    callback_data: Optional[str] = None
    handler: Optional[str] = None
    menu_type: Optional[MenuType] = None

class Menu:
    def __init__(self):
        self._items = {
            MenuType.MAIN: [
                MenuItem('📋 Создать документ', 'create_document', 'handle_create_document'),
                MenuItem('📁 Мои документы', 'my_documents', 'handle_my_documents'),
                MenuItem('⚙️ Настройки', 'settings', 'handle_settings'),
                MenuItem('ℹ️ Помощь', 'help', 'handle_help')
            ],
            MenuType.DOCUMENT_TYPES: [
                MenuItem('📃 Исковое заявление', 'claim', 'handle_document_type'),
                MenuItem('📄 Договор', 'contract', 'handle_document_type'),
                MenuItem('📑 Жалоба', 'complaint', 'handle_document_type'),
                MenuItem('📊 Ходатайство', 'motion', 'handle_document_type'),
                MenuItem('🔙 Назад', 'back', 'handle_back')
            ]
        }
    
    def get_items(self, menu_type: MenuType) -> List[MenuItem]:
        return self._items.get(menu_type, [])
    
    def find_item_by_callback(self, callback_data: str) -> Optional[MenuItem]:
        for items in self._items.values():
            for item in items:
                if item.callback_data == callback_data:
                    return item
        return None
    
    def find_item_by_text(self, text: str) -> Optional[MenuItem]:
        for items in self._items.values():
            for item in items:
                if item.text == text:
                    return item
        return None

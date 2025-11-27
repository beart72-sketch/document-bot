from typing import Dict, Optional
from domain.entities.menu import Menu, MenuType, MenuItem

class MenuService:
    def __init__(self):
        self.menu = Menu()
        self.user_states: Dict[int, MenuType] = {}
        self._setup_text_handlers()

    def _setup_text_handlers(self):
        """Настраивает маппинг текста кнопок на обработчики"""
        self.text_handlers = {
            "📋 Создать документ": "handle_create_document",
            "📂 Мои документы": "handle_my_documents", 
            "💳 Подписка": "handle_subscription",
            "💎 Премиум": "handle_premium",
            "⚙️ Настройки": "handle_settings",
            "🆘 Помощь": "handle_help",
            "🔙 Назад": "handle_back",
            "📃 Исковое заявление": "handle_document_type",
            "📄 Договор": "handle_document_type",
            "📑 Жалоба": "handle_document_type",
            "📊 Ходатайство": "handle_document_type"
        }

    def get_menu_items(self, menu_type: MenuType) -> list[MenuItem]:
        return self.menu.get_items(menu_type)

    def set_user_state(self, user_id: int, state: MenuType):
        self.user_states[user_id] = state

    def get_user_state(self, user_id: int) -> Optional[MenuType]:
        return self.user_states.get(user_id)

    def get_handler_for_text(self, text: str) -> Optional[str]:
        """Возвращает имя обработчика для текста кнопки"""
        return self.text_handlers.get(text)

    def get_handler_for_callback(self, callback_data: str) -> Optional[str]:
        item = self.menu.find_item_by_callback(callback_data)
        return item.handler if item else None

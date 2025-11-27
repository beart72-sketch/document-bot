from typing import Dict, Optional
from domain.entities.menu import Menu, MenuType, MenuItem

class MenuService:
    def __init__(self):
        self.menu = Menu()
        self.user_states: Dict[int, MenuType] = {}
    
    def get_menu_items(self, menu_type: MenuType) -> list[MenuItem]:
        return self.menu.get_items(menu_type)
    
    def set_user_state(self, user_id: int, state: MenuType):
        self.user_states[user_id] = state
    
    def get_user_state(self, user_id: int) -> Optional[MenuType]:
        return self.user_states.get(user_id)
    
    def get_handler_for_callback(self, callback_data: str) -> Optional[str]:
        item = self.menu.find_item_by_callback(callback_data)
        return item.handler if item else None
    
    def get_handler_for_text(self, text: str) -> Optional[str]:
        item = self.menu.find_item_by_text(text)
        return item.handler if item else None

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from domain.entities.menu import MenuType
from domain.services.menu_service import MenuService

class MainKeyboards:
    def __init__(self, menu_service: MenuService):
        self.menu_service = menu_service
    
    def create_reply_keyboard(self, menu_type: MenuType) -> ReplyKeyboardMarkup:
        """Создает reply-клавиатуру для указанного меню"""
        menu_items = self.menu_service.get_menu_items(menu_type)
        if not menu_items:
            return ReplyKeyboardMarkup(resize_keyboard=True)
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        # Группируем кнопки по 2 в ряд
        buttons = [KeyboardButton(item.text) for item in menu_items if item.text != '🔙 Назад']
        
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                markup.add(buttons[i], buttons[i+1])
            else:
                markup.add(buttons[i])
        
        # Добавляем "Назад" отдельно если есть
        back_item = next((item for item in menu_items if item.text == '🔙 Назад'), None)
        if back_item:
            markup.add(KeyboardButton(back_item.text))
        
        return markup

"""
Keyboard layouts for Telegram bot
"""

from .main_keyboards import (
    get_main_keyboard,
    get_document_types_keyboard, 
    get_subscription_keyboard,
    get_back_keyboard,
    get_cancel_keyboard
)

from .document_keyboards import (
    get_document_actions_keyboard,
    get_documents_list_keyboard
)

from .subscription_keyboards import (
    get_subscription_plans_keyboard,
    get_payment_keyboard
)

__all__ = [
    # main_keyboards
    'get_main_keyboard',
    'get_document_types_keyboard',
    'get_subscription_keyboard', 
    'get_back_keyboard',
    'get_cancel_keyboard',
    
    # document_keyboards  
    'get_document_actions_keyboard',
    'get_documents_list_keyboard',
    
    # subscription_keyboards
    'get_subscription_plans_keyboard',
    'get_payment_keyboard'
]

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_plans_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с тарифами подписки"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="🟢 Базовый - 299₽/мес",
        callback_data="subscription_plan:basic"
    ))
    builder.add(InlineKeyboardButton(
        text="🔵 Про - 599₽/мес", 
        callback_data="subscription_plan:pro"
    ))
    builder.add(InlineKeyboardButton(
        text="🟣 Премиум - 999₽/мес",
        callback_data="subscription_plan:premium"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="menu:subscription"
    ))
    
    builder.adjust(1)
    return builder.as_markup()


def get_payment_keyboard(plan: str) -> InlineKeyboardMarkup:
    """Клавиатура для оплаты"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="💳 Оплатить картой",
        callback_data=f"payment:card:{plan}"
    ))
    builder.add(InlineKeyboardButton(
        text="🤝 Оплатить через юкассу",
        callback_data=f"payment:yookassa:{plan}"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад к тарифам",
        callback_data="menu:subscription_plans"
    ))
    
    builder.adjust(1)
    return builder.as_markup()

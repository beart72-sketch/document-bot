"""Базовые обработчики команд (/start, /help)"""

import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from .keyboards import get_main_keyboard  # ← импортируем существующую функцию

logger = logging.getLogger(__name__)
base_router = Router()

@base_router.message(Command("start"))
async def start_command(message: Message):
    logger.info(f"👤 Пользователь {message.from_user.id} запустил бота")
    
    welcome_text = (
        "🤖 *Добро пожаловать в Document Bot!*\n\n"
        "Я помогу вам создавать и управлять документами.\n\n"
        "Выберите действие:"
    )
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()  # ← используем как есть
    )

@base_router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "🤖 *Главное меню*",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@base_router.message(Command("menu"))
async def menu_command(message: Message):
    await message.answer(
        "📋 *Главное меню*",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def register_base_handlers(dp):
    dp.include_router(base_router)
    logger.info("🟢 Базовые обработчики: /start, /help")

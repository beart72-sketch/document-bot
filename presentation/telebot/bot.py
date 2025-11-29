#!/usr/bin/env python3
"""
Telegram Bot Module
"""
import os
import sys
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from infrastructure.database.database import database
from core.config import Config

# Инициализация бота
bot = AsyncTeleBot(Config.TOKEN)

# Состояния пользователей (простейшая реализация)
user_states = {}

def create_main_menu():
    """Создает главное меню с кнопками"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = KeyboardButton('📋 Создать документ')
    btn2 = KeyboardButton('📁 Мои документы') 
    btn3 = KeyboardButton('⚙️ Настройки')
    btn4 = KeyboardButton('ℹ️ Помощь')
    
    markup.add(btn1, btn2, btn3, btn4)
    return markup

def create_document_types_menu():
    """Создает меню выбора типа документа"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = KeyboardButton('📃 Исковое заявление')
    btn2 = KeyboardButton('📄 Договор')
    btn3 = KeyboardButton('📑 Жалоба')
    btn4 = KeyboardButton('📊 Ходатайство')
    btn_back = KeyboardButton('🔙 Назад')
    
    markup.add(btn1, btn2, btn3, btn4, btn_back)
    return markup

def create_back_menu():
    """Создает меню только с кнопкой Назад"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('🔙 Назад'))
    return markup

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    print(f"📨 Получено /start от {message.from_user.id}")
    user_states[message.from_user.id] = 'main_menu'
    menu = create_main_menu()
    await bot.send_message(
        message.chat.id, 
        "👋 Добро пожаловать в Legal Document Bot!\n\n"
        "Выберите действие из меню ниже:",
        reply_markup=menu
    )

@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
async def back_to_main(message):
    """Обработчик кнопки Назад"""
    user_states[message.from_user.id] = 'main_menu'
    menu = create_main_menu()
    await bot.send_message(
        message.chat.id,
        "🔙 Возвращаемся в главное меню:",
        reply_markup=menu
    )

@bot.message_handler(func=lambda message: message.text == '📋 Создать документ')
async def create_document(message):
    print(f"📄 Создание документа от {message.from_user.id}")
    user_states[message.from_user.id] = 'document_type_selection'
    menu = create_document_types_menu()
    await bot.send_message(
        message.chat.id,
        "📋 Выберите тип документа:\n\n"
        "• 📃 Исковое заявление\n"
        "• 📄 Договор\n" 
        "• 📑 Жалоба\n"
        "• 📊 Ходатайство",
        reply_markup=menu
    )

@bot.message_handler(func=lambda message: message.text in ['📃 Исковое заявление', '📄 Договор', '📑 Жалоба', '📊 Ходатайство'])
async def handle_document_type(message):
    """Обработчик выбора типа документа"""
    doc_type = message.text
    user_id = message.from_user.id
    
    print(f"🎯 Выбран тип документа: {doc_type} от {user_id}")
    
    # Сохраняем выбор пользователя
    user_states[user_id] = f'creating_{doc_type[2:]}'
    
    await bot.send_message(
        message.chat.id,
        f"🔄 Начинаем создание: {doc_type}\n\n"
        f"Введите название документа:",
        reply_markup=create_back_menu()
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, '').startswith('creating_'))
async def handle_document_name(message):
    """Обработчик ввода названия документа"""
    user_id = message.from_user.id
    doc_type = user_states[user_id].replace('creating_', '')
    
    print(f"📝 Название документа '{message.text}' для типа {doc_type} от {user_id}")
    
    await bot.send_message(
        message.chat.id,
        f"✅ Документ '{message.text}' сохранен!\n\n"
        f"Тип: {doc_type}\n"
        f"Название: {message.text}\n\n"
        "Документ успешно создан и сохранен в базе данных.",
        reply_markup=create_main_menu()
    )
    
    # Возвращаем в главное меню
    user_states[user_id] = 'main_menu'

@bot.message_handler(func=lambda message: message.text == '📁 Мои документы')
async def my_documents(message):
    print(f"📁 Запрос документов от {message.from_user.id}")
    await bot.send_message(message.chat.id, "📂 Раздел моих документов в разработке...")

@bot.message_handler(func=lambda message: message.text == '⚙️ Настройки')
async def settings(message):
   (f"⚙️ Настройки от {message.from_user.id}")
    await bot.send_message(message.chat.id, "🔧 Раздел настроек в разработке...")

@bot.message_handler(func=lambda message: message.text == 'ℹ️ Помощь')
async def help_command(message):
    print(f"ℹ️ Помощь от {message.from_user.id}")
    await bot.send_message(message.chat.id, "📖 Раздел помощи в разработке...")

@bot.message_handler(func=lambda message: True)
async def echo_all(message):
    print(f"📨 Неизвестная команда: '{message.text}' от {message.from_user.id}")
    await bot.send_message(message.chat.id, "❌ Неизвестная команда. Используйте меню ниже:")

async def run_bot():
    """Запускает телеграм бота"""
    try:
        print(f"🔑 Токен: {Config.TOKEN[:10]}...")
        print(f"🤖 Бот: @Sud_keis_bot")
        print(f"🔗 Ссылка: https://t.me/Sud_keis_bot")
        
        # Проверяем подключение к базе данных
        if await database.health_check():
            print("✅ Подключение к базе данных установлено")
        else:
            print("❌ Ошибка подключения к базе данных")
            return
        
        # Создаем таблицы если их нет
        await database.create_tables()
        print("✅ Таблицы базы данных проверены/созданы")
        
        # Запускаем бота
        print("🤖 Бот запускается...")
        print("📱 Откройте Telegram и напишите боту @Sud_keis_bot")
        await bot.polling(non_stop=True)
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_bot())

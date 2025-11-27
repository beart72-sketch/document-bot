#!/usr/bin/env python3
"""
Запуск Telegram бота для юридических документов
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def main():
    """Запуск бота"""
    
    # Проверяем токен
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_actual_bot_token_here":
        print("❌ Токен бота не настроен!")
        print("📝 Получите токен у @BotFather и вставьте в .env файл")
        print("\n🎯 Как получить токен:")
        print("1. Напишите @BotFather в Telegram")
        print("2. Команда: /newbot")
        print("3. Придумайте имя бота")
        print("4. Скопируйте токен и вставьте в .env файл")
        return
    
    print("🤖 Запускаем Telegram бота...")
    
    # Запускаем бота из папки bot
    from bot.main import main as bot_main
    import asyncio
    asyncio.run(bot_main())

if __name__ == "__main__":
    main()

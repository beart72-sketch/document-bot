#!/usr/bin/env python3
"""
Утилита для проверки корректности конфигурации приложения.
Запускайте этот скрипт для проверки настроек перед запуском бота.
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from config import config, print_config_summary
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("📋 Убедитесь, что:")
    print("  1. Файл config.py существует в корневой директории")
    print("  2. В config.py есть переменная config")
    sys.exit(1)


def check_environment_variables():
    """Проверяет наличие всех необходимых переменных окружения"""
    print("🔍 Проверка переменных окружения...")
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "ADMIN_IDS"
    ]
    
    optional_vars = [
        "DB_NAME",
        "BACKUP_DIR", 
        "LOGS_DIR",
        "ENCRYPTION_KEY",
        "SALT",
        "LOG_LEVEL",
        "MAX_FILE_SIZE",
        "DEBUG"
    ]
    
    all_good = True
    
    # Проверяем обязательные переменные
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Маскируем чувствительные данные для вывода
            if "TOKEN" in var or "KEY" in var:
                masked_value = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: ОТСУТСТВУЕТ")
            all_good = False
    
    # Показываем опциональные переменные
    print("\n📋 Опциональные переменные:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var or "SALT" in var:
                masked_value = value[:5] + "..." + value[-3:] if len(value) > 10 else "***"
                print(f"  📝 {var}: {masked_value} (установлено)")
            else:
                print(f"  📝 {var}: {value} (установлено)")
        else:
            print(f"  📝 {var}: используется значение по умолчанию")
    
    return all_good


def check_configuration_values():
    """Проверяет корректность значений конфигурации"""
    print("\n🔍 Проверка значений конфигурации...")
    
    all_good = True
    
    try:
        # Проверяем токен бота
        if config.bot.TOKEN:
            if config.bot.TOKEN.count(':') == 1:
                token_preview = config.bot.TOKEN[:10] + "..." + config.bot.TOKEN[-5:]
                print(f"  ✅ Токен бота: корректный формат ({token_preview})")
            else:
                print(f"  ❌ Токен бота: неверный формат")
                all_good = False
        else:
            print(f"  ❌ Токен бота: отсутствует")
            all_good = False
        
        # Проверяем администраторов
        if config.bot.ADMIN_IDS:
            print(f"  ✅ Администраторы: {len(config.bot.ADMIN_IDS)} пользователей")
            for admin_id in config.bot.ADMIN_IDS:
                print(f"    👤 ID: {admin_id}")
        else:
            print(f"  ❌ Администраторы: не указаны")
            all_good = False
        
        # Проверяем базу данных
        print(f"  ✅ База данных: {config.database.DB_NAME}")
        print(f"  ✅ URL базы данных: {config.database.DB_URL}")
        
        # Проверяем директории
        print(f"  ✅ Директория бэкапов: {config.storage.BACKUP_DIR}")
        print(f"  ✅ Директория логов: {config.logging.LOGS_DIR}")
        
        # Проверяем лимиты
        print(f"  ✅ Макс. размер файла: {config.bot.MAX_FILE_SIZE / 1024 / 1024} MB")
        print(f"  ✅ Лимит документов: {config.storage.DEFAULT_DOCUMENT_LIMIT}")
        
        # Проверяем логирование
        print(f"  ✅ Уровень логирования: {config.logging.LOG_LEVEL}")
        print(f"  ✅ Режим отладки: {'ВКЛ' if config.DEBUG else 'ВЫКЛ'}")
        
    except Exception as e:
        print(f"  ❌ Ошибка в конфигурации: {e}")
        all_good = False
    
    return all_good


def check_file_permissions():
    """Проверяет доступность файлов и директорий"""
    print("\n🔍 Проверка прав доступа к файлам...")
    
    files_and_dirs_to_check = [
        config.storage.BACKUP_DIR,
        config.logging.LOGS_DIR,
        config.database.DB_NAME,
        ".env"
    ]
    
    all_good = True
    
    for path in files_and_dirs_to_check:
        if os.path.exists(path):
            if os.path.isdir(path):
                # Это директория
                if os.access(path, os.R_OK):
                    print(f"  ✅ {path}/: доступна для чтения")
                    if os.access(path, os.W_OK):
                        print(f"  ✅ {path}/: доступна для записи")
                    else:
                        print(f"  ⚠️  {path}/: нет прав на запись")
                        all_good = False
                else:
                    print(f"  ❌ {path}/: нет прав на чтение")
                    all_good = False
            else:
                # Это файл
                if os.access(path, os.R_OK):
                    print(f"  ✅ {path}: доступен для чтения")
                    if os.access(path, os.W_OK):
                        print(f"  ✅ {path}: доступен для записи")
                    else:
                        print(f"  ⚠️  {path}: нет прав на запись")
                else:
                    print(f"  ❌ {path}: нет прав на чтение")
                    all_good = False
        else:
            # Если файл/директория не существует, проверяем можем ли создать
            try:
                if path.endswith('/') or '.' not in os.path.basename(path):
                    # Скорее всего это директория
                    os.makedirs(path, exist_ok=True)
                    print(f"  ✅ {path}/: можно создать")
                    # Пытаемся удалить только если мы её создали
                    if not os.path.exists(path):
                        os.rmdir(path)
                else:
                    # Скорее всего это файл
                    with open(path, 'a'):
                        pass
                    print(f"  ✅ {path}: можно создать")
                    os.remove(path)
            except Exception as e:
                print(f"  ❌ {path}: нельзя создать ({e})")
                all_good = False
    
    return all_good


def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    print("\n🔍 Проверка зависимостей...")
    
    dependencies = [
        "aiogram",
        "aiofiles", 
        "dotenv"
    ]
    
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}: установлен")
        except ImportError:
            print(f"  ❌ {dep}: НЕ УСТАНОВЛЕН")
            all_good = False
    
    return all_good


def validate_configuration():
    """Запускает встроенную валидацию конфигурации"""
    print("\n🔍 Запуск встроенной валидации конфигурации...")
    
    try:
        errors = config.validate()
        
        if errors:
            for error in errors:
                if "⚠️" in error:
                    print(f"  ⚠️  {error}")
                else:
                    print(f"  ❌ {error}")
            # Предупреждения не считаем за ошибки
            critical_errors = [e for e in errors if "⚠️" not in e]
            return len(critical_errors) == 0
        else:
            print("  ✅ Конфигурация прошла встроенную проверку")
            return True
            
    except Exception as e:
        print(f"  ❌ Ошибка при валидации: {e}")
        return False


def main():
    """Основная функция проверки"""
    print("🚀 Запуск проверки конфигурации Document Bot")
    print("=" * 50)
    
    # Проверяем наличие .env файла
    if not os.path.exists(".env"):
        print("❌ Файл .env не найден!")
        print("📋 Создайте файл .env с следующими переменными:")
        print("""
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789
DB_NAME=document_bot.db
BACKUP_DIR=backups
LOGS_DIR=logs
ENCRYPTION_KEY=your_secure_encryption_key_here
SALT=your_salt_here
LOG_LEVEL=INFO
MAX_FILE_SIZE=52428800
DEBUG=false
        """)
        sys.exit(1)
    
    checks_passed = 0
    total_checks = 5
    
    # Выполняем проверки
    if check_environment_variables():
        checks_passed += 1
    
    if check_configuration_values():
        checks_passed += 1
        
    if check_file_permissions():
        checks_passed += 1
        
    if check_dependencies():
        checks_passed += 1
        
    if validate_configuration():
        checks_passed += 1
    
    # Выводим итоговую информацию
    print("\n" + "="*50)
    try:
        print_config_summary()
    except Exception as e:
        print(f"⚠️  Не удалось вывести сводку конфигурации: {e}")
    print("="*50)
    
    # Итоговый результат
    print(f"\n📊 Результаты проверки: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 Все проверки пройдены! Конфигурация корректна.")
        print("🤖 Бот готов к запуску.")
        return True
    else:
        print("❌ Обнаружены проблемы в конфигурации.")
        print("📋 Исправьте ошибки перед запуском бота.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Скрипт автосохранения бота на GitHub
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Выполняет команду и обрабатывает результат"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def auto_save(commit_message=None):
    """Автосохранение на GitHub"""
    print("🚀 Запуск автосохранения бота...")
    
    # Проверяем есть ли изменения
    if run_command("git diff-index --quiet HEAD --", "Проверка изменений"):
        print("📝 Нет изменений для сохранения")
        return True
    
    # Добавляем файлы
    if not run_command("git add .", "Добавление файлов"):
        return False
    
    # Создаем коммит
    if not commit_message:
        commit_message = f"autosave: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    commit_cmd = f'git commit -m "{commit_message}"'
    if not run_command(commit_cmd, "Создание коммита"):
        return False
    
    # Отправляем на GitHub
    if run_command("git push origin main", "Отправка на GitHub"):
        print("✅ Успешно сохранено на GitHub!")
        
        # Показываем последние коммиты
        print("\n📋 Последние коммиты:")
        subprocess.run("git log --oneline -5", shell=True)
        return True
    else:
        return False

if __name__ == "__main__":
    # Берем сообщение коммита из аргументов или используем стандартное
    commit_msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    
    success = auto_save(commit_msg)
    sys.exit(0 if success else 1)

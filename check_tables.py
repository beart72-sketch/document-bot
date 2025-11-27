#!/usr/bin/env python3
"""Проверка структуры таблиц"""
import sqlite3

def check_tables():
    conn = sqlite3.connect('legal_bot.db')
    cursor = conn.cursor()
    
    # Проверяем таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("📊 Таблицы в базе:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Проверяем структуру таблиц
    for table_name in ['users', 'documents', 'document_templates']:
        if (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"\n📋 Столбцы таблицы {table_name}:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_tables()

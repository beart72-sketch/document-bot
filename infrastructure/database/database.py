"""
Database Manager for Legal Bot
"""
import sqlite3
import logging
from typing import Optional, List, Dict, Any

class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица запросов анализа
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        document_text TEXT,
                        analysis_result TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление пользователя в базу"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding user: {e}")
    
    def save_analysis_request(self, user_id: int, document_text: str, analysis_result: str):
        """Сохранение запроса анализа"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analysis_requests (user_id, document_text, analysis_result)
                    VALUES (?, ?, ?)
                ''', (user_id, document_text, analysis_result))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error saving analysis request: {e}")

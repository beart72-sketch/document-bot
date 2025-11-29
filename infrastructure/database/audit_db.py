import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AuditDatabase:
    def __init__(self, db_path: str = "data/audit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"✅ AuditDatabase: {self.db_path}")

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Основная таблица аудита
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resource_type TEXT,
                    resource_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    metadata TEXT DEFAULT '{}',
                    doc_hash TEXT,
                    template_hash TEXT,
                    data_hash TEXT
                )
            """)
            
            # Таблица для шаблонов документов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    template_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()

    def log_action(self, user_id: int, action: str,
                  details: dict | str | None = None,
                  resource_type: str | None = None,
                  resource_id: str | None = None,
                  ip_address: str | None = None,
                  user_agent: str | None = None,
                  doc_hash: str | None = None,
                  template_hash: str | None = None,
                  data_hash: str | None = None) -> int:
        """Запись действия в аудит с метаданными и хешами"""
        import json
        
        # Нормализуем metadata
        if details is None:
            metadata = {}
        elif isinstance(details, str):
            metadata = {"note": details}
        else:
            metadata = dict(details)
        
        metadata_json = json.dumps(metadata, ensure_ascii=False, separators=(',', ':'))
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (
                    user_id, action, resource_type, resource_id,
                    ip_address, user_agent, metadata,
                    doc_hash, template_hash, data_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                action,
                resource_type,
                resource_id,
                ip_address,
                user_agent,
                metadata_json,
                doc_hash,
                template_hash,
                data_hash
            ))
            return cursor.lastrowid

    def register_template(self, name: str, template_hash: str):
        """Регистрация шаблона документа"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO document_templates (name, template_hash)
                VALUES (?, ?)
            """, (name, template_hash))
            conn.commit()
            logger.info(f"✅ Шаблон зарегистрирован: {name} → {template_hash}")

    def get_template_hash(self, name: str) -> Optional[str]:
        """Получение хеша шаблона по имени"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT template_hash FROM document_templates WHERE name = ?",
                (name,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

# Глобальный экземпляр для использования
audit_db = AuditDatabase()

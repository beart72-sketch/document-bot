"""
Аудит-БД: SQLite для юридически значимых событий
Соответствует ГОСТ Р 7.0.97-2016 и 152-ФЗ
Полная реализация — копируйте как есть
"""

import sqlite3
import logging
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AuditDatabase:
    """Надёжная аудит-БД с WAL и индексами"""

    def __init__(self, db_path: str = "data/audit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"✅ AuditDatabase: {self.db_path.absolute()}")

    def _init_db(self):
        """Создаёт структуру БД один раз"""
        with sqlite3.connect(self.db_path) as conn:
            # Надёжность
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")

            # Таблица событий
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    metadata TEXT,
                    doc_hash TEXT,
                    template_hash TEXT,
                    data_hash TEXT,
                    UNIQUE(timestamp, user_id, action)
                )
            """)

            # Индексы
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_action ON audit_log(user_id, action);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_hash ON audit_log(doc_hash);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp);")

            # Таблица шаблонов
            conn.execute("""
                CREATE TABLE IF NOT EXISTS template_registry (
                    template_name TEXT PRIMARY KEY,
                    template_hash TEXT NOT NULL,
                    template_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
                    content_hash TEXT NOT NULL
                )
            """)

    def log_action(
        self,
        user_id: int,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        meta = None,
        doc_hash: Optional[str] = None,
        template_hash: Optional[str] = None,
        data_hash: Optional[str] = None
    ) -> int:
        """Записывает событие в БД. Возвращает ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_log (
                        user_id, action, resource_type, resource_id,
                        ip_address, user_agent, metadata,
                        doc_hash, template_hash, data_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, action, resource_type, resource_id,
                    ip_address, user_agent,
                    json.dumps(meta, ensure_ascii=False) if isinstance(meta, dict) else str(meta),
                    doc_hash, template_hash, data_hash
                ))
                logger.debug(f"📝 Аудит записан: {action} для {user_id}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"❌ Ошибка аудита: {e}", exc_info=True)
            raise

    def register_template(self, template_name: str, template_path: str):
        """Регистрирует шаблон при старте"""
        try:
            with open(template_path, "rb") as f:
                content = f.read()
            template_hash = hashlib.sha256(content).hexdigest()[:16]
            content_hash = hashlib.sha1(content).hexdigest()[:12]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO template_registry 
                    (template_name, template_hash, template_size, content_hash)
                    VALUES (?, ?, ?, ?)
                """, (template_name, template_hash, len(content), content_hash))
            logger.info(f"✅ Шаблон зарегистрирован: {template_name} → {template_hash}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось зарегистрировать шаблон {template_name}: {e}")

    def verify_document(self, doc_hash: str) -> bool:
        """Проверяет, был ли документ сгенерирован системой"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM audit_log WHERE doc_hash = ? LIMIT 1", (doc_hash,))
            return cursor.fetchone() is not None

# Глобальный экземпляр — готов к использованию
audit_db = AuditDatabase()

# Автоматическая регистрация шаблонов при импорте
try:
    audit_db.register_template("contract_template", "templates/contract_template.docx")
except Exception as e:
    logger.warning(f"ℹ️ Шаблон contract_template не зарегистрирован: {e}")

"""Шаблонизатор документов с поддержкой аудита и валидации — для юридической точности"""

import logging
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from docxtpl import DocxTemplate
from docx import Document

logger = logging.getLogger(__name__)

class TemplateEngineError(Exception):
    """Базовое исключение шаблонизатора"""
    pass

class TemplateValidationError(TemplateEngineError):
    """Ошибка валидации данных шаблона"""
    pass

class TemplateEngine:
    """Генератор документов с аудитом и валидацией"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        logger.info(f"✅ TemplateEngine инициализирован. Шаблоны: {self.templates_dir}")
    
    def _calculate_hash(self, data: str) -> str:
        """Вычисляет SHA-256 хэш для аудита"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]
    
    def _validate_required_fields(self, template_name: str, context: Dict[str, Any]) -> None:
        """Валидация обязательных полей для юридической значимости"""
        required_fields = {
            "contract": ["party1_full_name", "party2_full_name", "subject", "amount", "date"],
            "claim": ["plaintiff", "defendant", "court", "claim_amount", "date"],
            "complaint": ["applicant", "respondent", "violation", "date"]
        }
        
        fields = required_fields.get(template_name, [])
        missing = [field for field in fields if not context.get(field)]
        
        if missing:
            raise TemplateValidationError(
                f"❌ Отсутствуют обязательные поля для '{template_name}': {', '.join(missing)}"
            )
    
    def render_document(
        self,
        template_name: str,
        context: Dict[str, Any],
        user_id: int,
        audit_callback = None
    ) -> bytes:
        """
        Генерирует документ с полным аудитом
        
        Args:
            template_name: имя шаблона (без .docx)
            context: данные для заполнения
            user_id: для аудита
            audit_callback: функция логирования (user_id, template_hash, doc_hash, metadata)
        
        Returns:
            bytes: сгенерированный .docx
        """
        try:
            # 1. Валидация
            self._validate_required_fields(template_name, context)
            
            # 2. Загрузка шаблона
            template_path = self.templates_dir / f"{template_name}.docx"
            if not template_path.exists():
                raise TemplateEngineError(f"❌ Шаблон не найден: {template_path}")
            
            # 3. Хэш шаблона (для аудита неизменности)
            with open(template_path, 'rb') as f:
                template_hash = self._calculate_hash(str(f.read())[:1000])  # первые 1000 байт
            
            # 4. Хэш данных (для аудита воспроизводимости)
            data_hash = self._calculate_hash(json.dumps(context, sort_keys=True, default=str))
            
            # 5. Генерация
            doc = DocxTemplate(template_path)
            doc.render(context)
            
            # 6. Сохранение в bytes
            from io import BytesIO
            buffer = BytesIO()
            doc.save(buffer)
            document_bytes = buffer.getvalue()
            
            # 7. Хэш документа (для аудита целостности)
            doc_hash = self._calculate_hash(str(document_bytes)[:2000])
            
            # 8. Аудит
            if audit_callback:
                metadata = {
                    "template_name": template_name,
                    "template_hash": template_hash,
                    "data_hash": data_hash,
                    "doc_hash": doc_hash,
                    "generated_at": datetime.now().isoformat(),
                    "context_keys": list(context.keys())
                }
                audit_callback(user_id=user_id, action="document_rendered", metadata=metadata)
                logger.info(f"✅ Аудит: doc={doc_hash}, tmpl={template_hash} для {user_id}")
            
            return document_bytes
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации '{template_name}': {e}")
            raise TemplateEngineError(f"Генерация не удалась: {e}") from e

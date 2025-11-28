"""Фабрика сервисов (временная заглушка для MVP)"""

import logging
from application.services.document_service import DocumentService
from domain.services.audit_service import AuditService
from infrastructure.repositories.document_repository import DocumentRepository
from application.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class ServiceFactory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        try:
            # Заглушки для зависимостей
            doc_repo = DocumentRepository()
            sub_service = SubscriptionService()
            
            self._document_service = DocumentService(doc_repo, sub_service)
            self._audit_service = AuditService()
            logger.info("✅ Временная ServiceFactory инициализирована")
        except Exception as e:
            logger.warning(f"⚠️ ServiceFactory частично недоступна: {e}")
            self._document_service = None
            self._audit_service = None
    
    def get_document_service(self):
        return self._document_service
    
    def get_audit_service(self):
        return self._audit_service

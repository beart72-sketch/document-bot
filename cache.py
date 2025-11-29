"""
Модуль для кэширования данных и частых запросов.
Ускоряет работу бота за счёт уменьшения повторных операций.
"""

import asyncio
import time
from typing import Any, Optional, Dict, List
from functools import wraps
import logging
from core.config import config

logger = logging.getLogger(__name__)


class Cache:
    """Класс для управления кэшем в памяти"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 300  # 5 минут по умолчанию
        self._cleanup_interval = 60  # Очистка каждую минуту
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Сохраняет значение в кэш с TTL"""
        ttl = ttl or self._default_ttl
        expire_time = time.time() + ttl
        
        self._cache[key] = {
            'value': value,
            'expire_time': expire_time,
            'created_at': time.time()
        }
        
        logger.debug(f"Кэш установлен: {key} (TTL: {ttl}сек)")
    
    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша или None если не найдено или просрочено"""
        if key not in self._cache:
            return None
            
        item = self._cache[key]
        
        # Проверяем не просрочен ли кэш
        if time.time() > item['expire_time']:
            del self._cache[key]
            logger.debug(f"Кэш просрочен: {key}")
            return None
            
        logger.debug(f"Кэш получен: {key}")
        return item['value']
    
    def delete(self, key: str) -> bool:
        """Удаляет значение из кэша"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Кэш удалён: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Очищает весь кэш"""
        self._cache.clear()
        logger.info("Кэш полностью очищен")
    
    def cleanup_expired(self) -> int:
        """Удаляет просроченные записи и возвращает количество удалённых"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time > item['expire_time']
        ]
        
        for key in expired_keys:
            del self._cache[key]
            
        if expired_keys:
            logger.debug(f"Очищено просроченных записей: {len(expired_keys)}")
            
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша"""
        current_time = time.time()
        active_items = {
            key: item for key, item in self._cache.items()
            if current_time <= item['expire_time']
        }
        
        return {
            'total_items': len(self._cache),
            'active_items': len(active_items),
            'expired_items': len(self._cache) - len(active_items),
            'memory_usage': f"{sum(len(str(v)) for v in self._cache.values())} chars"
        }


class AsyncCacheManager:
    """Менеджер асинхронного кэширования с поддержкой разных бэкендов"""
    
    def __init__(self):
        self.memory_cache = Cache()
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start_cleanup_task(self):
        """Запускает фоновую задачу очистки просроченного кэша"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_worker())
            logger.info("Фоновая очистка кэша запущена")
    
    async def stop_cleanup_task(self):
        """Останавливает фоновую задачу очистки"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Фоновая очистка кэша остановлена")
    
    async def _cleanup_worker(self):
        """Фоновая задача для очистки просроченного кэша"""
        while True:
            try:
                await asyncio.sleep(self.memory_cache._cleanup_interval)
                cleaned = self.memory_cache.cleanup_expired()
                if cleaned > 0:
                    logger.info(f"Фоновая очистка: удалено {cleaned} записей")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в фоновой очистке кэша: {e}")
                await asyncio.sleep(10)  # Ждём перед повторной попыткой
    
    def cache_result(
        self, 
        ttl: int = 300, 
        key_prefix: str = "",
        ignore_args: List[int] = None
    ):
        """
        Декоратор для кэширования результатов функций
        
        Args:
            ttl: Время жизни кэша в секундах
            key_prefix: Префикс для ключа кэша
            ignore_args: Индексы аргументов которые игнорируются при создании ключа
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Создаём ключ кэша на основе аргументов
                cache_key_parts = [key_prefix, func.__name__]
                
                # Добавляем аргументы (игнорируя указанные)
                if args:
                    for i, arg in enumerate(args):
                        if ignore_args and i in ignore_args:
                            continue
                        cache_key_parts.append(str(arg))
                
                # Добавляем ключевые аргументы
                if kwargs:
                    for k, v in sorted(kwargs.items()):
                        cache_key_parts.append(f"{k}={v}")
                
                cache_key = ":".join(cache_key_parts)
                
                # Пробуем получить из кэша
                cached_result = self.memory_cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Кэш попадание для {func.__name__}")
                    return cached_result
                
                # Выполняем функцию если нет в кэше
                logger.debug(f"Кэш промах для {func.__name__}, выполняем функцию")
                result = await func(*args, **kwargs)
                
                # Сохраняем результат в кэш
                self.memory_cache.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str):
        """Удаляет все ключи кэша соответствующие паттерну"""
        keys_to_delete = [
            key for key in self.memory_cache._cache.keys()
            if pattern in key
        ]
        
        for key in keys_to_delete:
            self.memory_cache.delete(key)
        
        logger.info(f"Инвалидировано ключей по паттерну '{pattern}': {len(keys_to_delete)}")
        return len(keys_to_delete)


# Сначала создаём менеджер кэша
cache_manager = AsyncCacheManager()


# Теперь создаём специализированные кэши
class UserDataCache:
    """Кэш для данных пользователей"""
    
    def __init__(self):
        self.user_ttl = 600  # 10 минут для пользовательских данных
    
    @cache_manager.cache_result(ttl=600, key_prefix="user")
    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Получает профиль пользователя (пример)"""
        # В реальной реализации здесь был бы запрос к БД
        logger.info(f"Запрос к БД для пользователя {user_id}")
        return {"id": user_id, "name": f"User_{user_id}", "documents_count": 0}
    
    def invalidate_user_cache(self, user_id: int):
        """Инвалидирует кэш для конкретного пользователя"""
        return cache_manager.invalidate_pattern(f"user:get_user_profile:{user_id}")


class DocumentCache:
    """Кэш для операций с документами"""
    
    def __init__(self):
        self.document_ttl = 300  # 5 минут для документов
    
    @cache_manager.cache_result(ttl=300, key_prefix="doc")
    async def get_document_info(self, doc_id: str) -> Dict[str, Any]:
        """Получает информацию о документе (пример)"""
        # В реальной реализации здесь был бы запрос к БД
        logger.info(f"Запрос к БД для документа {doc_id}")
        return {"id": doc_id, "title": f"Document_{doc_id}", "size": 1024}
    
    @cache_manager.cache_result(ttl=3600, key_prefix="doc_list")  # 1 час для списков
    async def get_user_documents(self, user_id: int, page: int = 1) -> List[Dict]:
        """Получает список документов пользователя (пример)"""
        # В реальной реализации здесь был бы запрос к БД
        logger.info(f"Запрос к БД для документов пользователя {user_id}, страница {page}")
        return [{"id": f"doc_{i}", "title": f"Document {i}"} for i in range(5)]
    
    def invalidate_document_cache(self, doc_id: str):
        """Инвалидирует кэш для конкретного документа"""
        return cache_manager.invalidate_pattern(f"doc:get_document_info:{doc_id}")
    
    def invalidate_user_documents_cache(self, user_id: int):
        """Инвалидирует кэш списка документов пользователя"""
        return cache_manager.invalidate_pattern(f"doc_list:get_user_documents:{user_id}")


# Создаём экземпляры специализированных кэшей
user_cache = UserDataCache()
document_cache = DocumentCache()


async def initialize_caching():
    """Инициализирует систему кэширования"""
    if config.DEBUG:
        logger.info("Инициализация системы кэширования...")
    
    # Запускаем фоновую очистку
    await cache_manager.start_cleanup_task()
    
    if config.DEBUG:
        logger.info("✅ Система кэширования инициализирована")


async def shutdown_caching():
    """Останавливает систему кэширования"""
    await cache_manager.stop_cleanup_task()
    cache_manager.memory_cache.clear()
    logger.info("✅ Система кэширования остановлена")

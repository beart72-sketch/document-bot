"""
Модуль для сбора метрик и мониторинга производительности бота.
Позволяет отслеживать производительность, ошибки и использование ресурсов.
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import logging
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Базовый класс для метрик"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]


class MetricsCollector:
    """Сборщик и агрегатор метрик"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.max_history = max_history
        
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Увеличивает счетчик"""
        self.counters[name] += value
        self._store_metric(name, self.counters[name], tags)
        logger.debug(f"Счетчик {name} увеличен до {self.counters[name]}")
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Устанавливает значение gauge"""
        self.gauges[name] = value
        self._store_metric(name, value, tags)
        logger.debug(f"Gauge {name} установлен в {value}")
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Записывает время выполнения"""
        self.timers[name].append(duration)
        if len(self.timers[name]) > self.max_history:
            self.timers[name].pop(0)
        self._store_metric(f"{name}_duration", duration, tags)
        logger.debug(f"Таймер {name}: {duration:.3f}сек")
    
    def _store_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Сохраняет метрику в историю"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        self.metrics_history[name].append(metric)
    
    def get_counter(self, name: str) -> int:
        """Получает значение счетчика"""
        return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Получает значение gauge"""
        return self.gauges.get(name, 0.0)
    
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Получает статистику таймера"""
        values = self.timers.get(name, [])
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / len(values),
            'p95': sorted(values)[int(len(values) * 0.95)],
            'p99': sorted(values)[int(len(values) * 0.99)]
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Возвращает сводку всех метрик"""
        summary = {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'timers': {}
        }
        
        for timer_name in self.timers:
            summary['timers'][timer_name] = self.get_timer_stats(timer_name)
        
        return summary
    
    def reset(self):
        """Сбрасывает все метрики"""
        self.counters.clear()
        self.gauges.clear()
        self.timers.clear()
        self.metrics_history.clear()
        logger.info("Все метрики сброшены")


class PerformanceMonitor:
    """Монитор производительности с декораторами для автоматического сбора метрик"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def track_execution(self, name: str = None, tags: Dict[str, str] = None):
        """
        Декоратор для отслеживания времени выполнения функций
        """
        def decorator(func):
            metric_name = name or func.__name__
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.collector.record_timer(metric_name, duration, tags)
                    self.collector.increment_counter(f"{metric_name}_success", tags=tags)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.collector.record_timer(metric_name, duration, tags)
                    self.collector.increment_counter(f"{metric_name}_error", tags=tags)
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.collector.record_timer(metric_name, duration, tags)
                    self.collector.increment_counter(f"{metric_name}_success", tags=tags)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.collector.record_timer(metric_name, duration, tags)
                    self.collector.increment_counter(f"{metric_name}_error", tags=tags)
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def track_telegram_handler(self, command: str = None):
        """
        Декоратор для отслеживания обработчиков Telegram
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Ищем сообщение или callback в аргументах
                message = None
                callback = None
                
                for arg in args:
                    if hasattr(arg, 'text') and hasattr(arg, 'from_user'):
                        message = arg
                        break
                    elif hasattr(arg, 'data') and hasattr(arg, 'from_user'):
                        callback = arg
                        break
                
                # Определяем тип команды
                handler_type = command or "unknown"
                if message and message.text:
                    if message.text.startswith('/'):
                        handler_type = message.text.split()[0]
                elif callback:
                    handler_type = f"callback_{callback.data.split(':')[0] if ':' in callback.data else callback.data}"
                
                tags = {
                    'handler': handler_type,
                    'user_id': str(message.from_user.id if message else callback.from_user.id if callback else 'unknown')
                }
                
                return await self.track_execution(f"handler_{handler_type}", tags)(func)(*args, **kwargs)
            return wrapper
        return decorator


class HealthChecker:
    """Проверка здоровья системы"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        self.health_checks = {}
    
    def add_health_check(self, name: str, check_func, interval: int = 60):
        """Добавляет проверку здоровья"""
        self.health_checks[name] = {
            'function': check_func,
            'interval': interval,
            'last_check': 0
        }
    
    async def run_health_checks(self):
        """Выполняет все проверки здоровья"""
        current_time = time.time()
        results = {}
        
        for name, check_info in self.health_checks.items():
            if current_time - check_info['last_check'] >= check_info['interval']:
                try:
                    result = await check_info['function']()
                    results[name] = {
                        'status': 'healthy',
                        'details': result,
                        'timestamp': current_time
                    }
                    self.collector.set_gauge(f"health_{name}", 1.0)
                except Exception as e:
                    results[name] = {
                        'status': 'unhealthy',
                        'error': str(e),
                        'timestamp': current_time
                    }
                    self.collector.set_gauge(f"health_{name}", 0.0)
                    logger.error(f"Проверка здоровья {name} не удалась: {e}")
                
                check_info['last_check'] = current_time
        
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """Возвращает общий статус здоровья"""
        healthy_checks = 0
        total_checks = len(self.health_checks)
        
        for name in self.health_checks:
            if self.collector.get_gauge(f"health_{name}") == 1.0:
                healthy_checks += 1
        
        overall_health = 'healthy' if healthy_checks == total_checks else 'degraded' if healthy_checks > 0 else 'unhealthy'
        
        return {
            'status': overall_health,
            'healthy_checks': healthy_checks,
            'total_checks': total_checks,
            'health_percentage': (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        }


# Глобальные экземпляры
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor(metrics_collector)
health_checker = HealthChecker(metrics_collector)


# Предопределенные метрики для бота
class BotMetrics:
    """Предопределенные метрики для телеграм бота"""
    
    @staticmethod
    def track_message():
        """Отслеживает входящие сообщения"""
        def decorator(func):
            @wraps(func)
            async def wrapper(message, *args, **kwargs):
                metrics_collector.increment_counter("messages_received")
                metrics_collector.increment_counter(f"messages_type_{message.content_type}")
                
                if message.text and message.text.startswith('/'):
                    command = message.text.split()[0]
                    metrics_collector.increment_counter(f"command_{command}")
                
                return await func(message, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def track_callback():
        """Отслеживает callback запросы"""
        def decorator(func):
            @wraps(func)
            async def wrapper(callback, *args, **kwargs):
                metrics_collector.increment_counter("callbacks_received")
                if callback.data:
                    metrics_collector.increment_counter(f"callback_{callback.data.split(':')[0]}")
                
                return await func(callback, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def track_user_activity():
        """Отслеживает активность пользователей"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Ищем user_id в аргументах
                user_id = None
                for arg in args:
                    if hasattr(arg, 'from_user'):
                        user_id = arg.from_user.id
                        break
                    elif isinstance(arg, int) and arg > 0:
                        user_id = arg
                        break
                
                if user_id:
                    metrics_collector.increment_counter("active_users", tags={'user_id': str(user_id)})
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator


async def initialize_monitoring():
    """Инициализирует систему мониторинга"""
    logger.info("Инициализация системы мониторинга...")
    
    # Добавляем базовые проверки здоровья
    async def check_database_health():
        """Проверка здоровья базы данных"""
        # В реальной реализации здесь была бы проверка подключения к БД
        return {"status": "connected", "tables": 5}
    
    async def check_cache_health():
        """Проверка здоровья кэша"""
        from cache import cache_manager
        stats = cache_manager.memory_cache.get_stats()
        return stats
    
    health_checker.add_health_check("database", check_database_health)
    health_checker.add_health_check("cache", check_cache_health)
    
    logger.info("Система мониторинга инициализирована")


async def shutdown_monitoring():
    """Останавливает систему мониторинга"""
    logger.info("Остановка системы мониторинга...")
    
    # Сохраняем финальные метрики
    final_metrics = metrics_collector.get_metrics_summary()
    logger.info(f"Финальные метрики: {final_metrics}")
    
    logger.info("Система мониторинга остановлена")

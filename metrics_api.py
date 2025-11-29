"""
Простой API для просмотра метрик через Telegram команды
"""

import json
from typing import Dict, Any
from aiogram import types
from metrics import metrics_collector, health_checker, performance_monitor
from core.config import config


class MetricsAPI:
    """API для работы с метриками через Telegram"""
    
    def __init__(self):
        self.authorized_users = config.get_admin_ids()
    
    def is_authorized(self, user_id: int) -> bool:
        """Проверяет авторизацию пользователя"""
        return user_id in self.authorized_users
    
    async def get_metrics_summary(self, message: types.Message) -> str:
        """Возвращает сводку метрик"""
        if not self.is_authorized(message.from_user.id):
            return "❌ У вас нет прав для просмотра метрик."
        
        summary = metrics_collector.get_metrics_summary()
        
        response = [
            "📊 **Сводка метрик бота**",
            "",
            "**Счетчики:**",
        ]
        
        # Добавляем счетчики
        for name, value in summary['counters'].items():
            response.append(f"  {name}: {value}")
        
        response.extend(["", "**Таймеры:**"])
        
        # Добавляем таймеры
        for name, stats in summary['timers'].items():
            if stats:
                response.append(f"  {name}:")
                response.append(f"    count: {stats['count']}")
                response.append(f"    mean: {stats['mean']:.3f}s")
                response.append(f"    p95: {stats['p95']:.3f}s")
        
        response.extend(["", "**Система:**"])
        
        # Добавляем системную информацию
        health_status = health_checker.get_health_status()
        response.append(f"  Здоровье: {health_status['status']}")
        response.append(f"  Проверок: {health_status['healthy_checks']}/{health_status['total_checks']}")
        
        return "\n".join(response)
    
    async def get_health_status(self, message: types.Message) -> str:
        """Возвращает статус здоровья системы"""
        if not self.is_authorized(message.from_user.id):
            return "❌ У вас нет прав для просмотра статуса здоровья."
        
        health_status = health_checker.get_health_status()
        
        response = [
            "🏥 **Статус здоровья системы**",
            "",
            f"**Общий статус:** {health_status['status'].upper()}",
            f"**Проверки:** {health_status['healthy_checks']}/{health_status['total_checks']}",
            f"**Процент здоровья:** {health_status['health_percentage']:.1f}%",
            "",
            "**Детали:**"
        ]
        
        # Получаем детали проверок
        health_details = await health_checker.run_health_checks()
        for name, details in health_details.items():
            status_icon = "✅" if details['status'] == 'healthy' else "❌"
            response.append(f"  {status_icon} {name}: {details['status']}")
            if 'details' in details:
                response.append(f"     {json.dumps(details['details'], default=str)}")
        
        return "\n".join(response)
    
    async def reset_metrics(self, message: types.Message) -> str:
        """Сбрасывает метрики"""
        if not self.is_authorized(message.from_user.id):
            return "❌ У вас нет прав для сброса метрик."
        
        metrics_collector.reset()
        return "✅ Все метрики сброшены."
    
    async def get_performance_report(self, message: types.Message) -> str:
        """Возвращает отчет о производительности"""
        if not self.is_authorized(message.from_user.id):
            return "❌ У вас нет прав для просмотра отчета о производительности."
        
        summary = metrics_collector.get_metrics_summary()
        
        # Находим самые медленные обработчики
        slow_handlers = []
        for name, stats in summary['timers'].items():
            if stats and name.startswith('handler_'):
                slow_handlers.append((name, stats['p95']))
        
        # Сортируем по убыванию времени выполнения
        slow_handlers.sort(key=lambda x: x[1], reverse=True)
        
        response = [
            "⚡ **Отчет о производительности**",
            "",
            "**Самые медленные обработчики:**"
        ]
        
        for i, (handler, p95_time) in enumerate(slow_handlers[:5], 1):
            response.append(f"  {i}. {handler}: {p95_time:.3f}s")
        
        # Общая статистика
        total_messages = summary['counters'].get('messages_received', 0)
        total_callbacks = summary['counters'].get('callbacks_received', 0)
        
        response.extend([
            "",
            "**Общая статистика:**",
            f"  Сообщений обработано: {total_messages}",
            f"  Callback-ов обработано: {total_callbacks}",
            f"  Активных пользователей: {summary['counters'].get('active_users', 0)}"
        ])
        
        return "\n".join(response)


# Глобальный экземпляр API
metrics_api = MetricsAPI()

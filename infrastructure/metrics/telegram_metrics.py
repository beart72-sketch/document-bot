"""Telegram-specific metrics."""
import time
import logging
from typing import Optional, Dict, Any
from aiogram import types

from .base_metrics import MetricsCollector

logger = logging.getLogger(__name__)

class TelegramMetrics(MetricsCollector):
    """Telegram-specific metrics collector."""
    
    def __init__(self):
        super().__init__()
        self.user_actions = {}
        self.handler_stats = {}
    
    def record_user_action(self, user_id: int, action_type: str, success: bool = True):
        """Record user action with success/failure."""
        if user_id not in self.user_actions:
            self.user_actions[user_id] = {'success': 0, 'failed': 0, 'actions': {}}
        
        if success:
            self.user_actions[user_id]['success'] += 1
        else:
            self.user_actions[user_id]['failed'] += 1
        
        # Track specific action types
        action_key = f"{action_type}_{'success' if success else 'failed'}"
        self.user_actions[user_id]['actions'][action_key] = \
            self.user_actions[user_id]['actions'].get(action_key, 0) + 1
        
        if self.config['log_metrics']:
            status = "✅" if success else "❌"
            logger.debug(f"👤 User action: {user_id} - {action_type} {status}")
    
    def record_handler_execution(self, handler_name: str, execution_time: float, success: bool = True):
        """Record handler execution statistics."""
        if handler_name not in self.handler_stats:
            self.handler_stats[handler_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0
            }
        
        stats = self.handler_stats[handler_name]
        stats['total_executions'] += 1
        stats['total_time'] += execution_time
        
        if execution_time < stats['min_time']:
            stats['min_time'] = execution_time
        if execution_time > stats['max_time']:
            stats['max_time'] = execution_time
        
        if success:
            stats['successful_executions'] += 1
        
        # Also record in base metrics
        self.record_handler_time(handler_name, execution_time)
    
    def get_handler_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed handler statistics."""
        stats = {}
        for handler_name, handler_data in self.handler_stats.items():
            if handler_data['total_executions'] > 0:
                avg_time = handler_data['total_time'] / handler_data['total_executions']
                success_rate = handler_data['successful_executions'] / handler_data['total_executions']
                
                stats[handler_name] = {
                    'total_executions': handler_data['total_executions'],
                    'success_rate': success_rate,
                    'avg_time_seconds': avg_time,
                    'min_time_seconds': handler_data['min_time'],
                    'max_time_seconds': handler_data['max_time']
                }
        
        return stats
    
    def get_user_activity_summary(self) -> Dict[str, Any]:
        """Get user activity summary."""
        total_actions = 0
        total_success = 0
        total_failed = 0
        active_users = len(self.user_actions)
        
        for user_data in self.user_actions.values():
            total_success += user_data['success']
            total_failed += user_data['failed']
        
        total_actions = total_success + total_failed
        success_rate = total_success / max(total_actions, 1)
        
        return {
            'active_users': active_users,
            'total_actions': total_actions,
            'successful_actions': total_success,
            'failed_actions': total_failed,
            'success_rate': success_rate
        }
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics including Telegram-specific data."""
        base_summary = self.get_metrics_summary()
        handler_stats = self.get_handler_stats()
        user_activity = self.get_user_activity_summary()
        
        detailed_metrics = {
            **base_summary,
            'handler_statistics': handler_stats,
            'user_activity': user_activity,
            'telegram_specific': {
                'user_actions_tracked': len(self.user_actions),
                'handlers_tracked': len(self.handler_stats)
            }
        }
        
        return detailed_metrics

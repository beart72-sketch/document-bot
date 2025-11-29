"""Metrics collection decorators."""
import functools
import time
import logging
from typing import Any, Callable, Optional

from .telegram_metrics import TelegramMetrics

logger = logging.getLogger(__name__)

# Global metrics collector
_metrics = TelegramMetrics()

def track_performance(metric_name: Optional[str] = None):
    """
    Decorator for tracking function performance.
    
    Args:
        metric_name: Custom metric name (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        actual_metric_name = metric_name or func.__name__
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                execution_time = time.time() - start_time
                _metrics.record_handler_execution(actual_metric_name, execution_time, success)
                
                if _metrics.config['log_metrics']:
                    status = "✅" if success else "❌"
                    logger.debug(f"📊 Performance: {actual_metric_name} {status} in {execution_time:.3f}s")
        
        return wrapper
    return decorator

def track_user_action(action_name: Optional[str] = None):
    """
    Decorator for tracking user actions.
    
    Args:
        action_name: Custom action name (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        actual_action_name = action_name or func.__name__
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract user_id from Telegram message/callback
            user_id = None
            if args and hasattr(args[0], 'from_user') and hasattr(args[0].from_user, 'id'):
                user_id = args[0].from_user.id
            
            success = True
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                if user_id:
                    _metrics.record_user_action(user_id, actual_action_name, success)
        
        return wrapper
    return decorator

def track_telegram_message(message_type: str = "message"):
    """
    Decorator for tracking Telegram messages/callbacks.
    
    Args:
        message_type: Type of message ("message" or "callback")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract user_id
            user_id = None
            if args and hasattr(args[0], 'from_user') and hasattr(args[0].from_user, 'id'):
                user_id = args[0].from_user.id
            
            # Record metric based on type
            if message_type == "message":
                _metrics.record_message(user_id)
            elif message_type == "callback":
                _metrics.record_callback(user_id)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def with_metrics(metric_name: Optional[str] = None):
    """
    Combined decorator for comprehensive metrics tracking.
    Tracks performance, user actions, and errors.
    """
    def decorator(func: Callable) -> Callable:
        actual_metric_name = metric_name or func.__name__
        
        # Apply all decorators
        @track_performance(actual_metric_name)
        @track_user_action(actual_metric_name)
        @track_telegram_message()  # Will detect type automatically
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

"""Cache decorators."""
import functools
import inspect
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

def cached(key_pattern: str, ttl: int = 3600):
    """
    Decorator for caching function results.
    
    Args:
        key_pattern: Key pattern (can contain {func_name}, {args}, {kwargs})
        ttl: Cache TTL in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Skip caching if no cache in context
            if not args or not hasattr(args[0], 'cache'):
                return await func(*args, **kwargs)
                
            # Generate cache key
            cache_key = key_pattern.format(
                func_name=func.__name__,
                args=str(args[1:]) if len(args) > 1 else '',
                kwargs=str(kwargs) if kwargs else ''
            )
            
            # Try to get from cache
            try:
                cache = args[0].cache
                cached_result = await cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"✅ Cache hit: {cache_key}")
                    return cached_result
                else:
                    logger.debug(f"❌ Cache miss: {cache_key}")
            except Exception as e:
                logger.warning(f"⚠️ Cache get error for {cache_key}: {e}")
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            try:
                if hasattr(args[0], 'cache'):
                    await args[0].cache.set(cache_key, result, ttl)
                    logger.debug(f"💾 Cached: {cache_key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"⚠️ Cache set error for {cache_key}: {e}")
            
            return result
        return wrapper
    return decorator

def cache_user_data(ttl: int = 1800):
    """Decorator for caching user-specific data."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract user_id from arguments
            user_id = "unknown"
            if args and hasattr(args[0], 'from_user') and hasattr(args[0].from_user, 'id'):
                user_id = args[0].from_user.id
            elif 'user_id' in kwargs:
                user_id = kwargs['user_id']
            
            key_pattern = f"user:{user_id}:{func.__name__}"
            cached_decorator = cached(key_pattern, ttl)
            return await cached_decorator(func)(*args, **kwargs)
        return wrapper
    return decorator

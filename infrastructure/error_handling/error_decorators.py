"""Error handling decorators."""
import functools
import logging
from typing import Any, Callable, Optional

from .telegram_errors import TelegramErrorHandler

logger = logging.getLogger(__name__)

# Global error handler instance
_error_handler = TelegramErrorHandler()

def handle_errors(
    default_message: str = "⚠️ Произошла ошибка. Попробуйте позже.",
    log_error: bool = True,
    re_raise: bool = False
):
    """
    Decorator for error handling in async functions.
    
    Args:
        default_message: Default message to send on error
        log_error: Whether to log the error
        re_raise: Whether to re-raise the error after handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Extract message/callback from args for Telegram errors
                message_or_callback = None
                if args and hasattr(args[0], 'answer') or hasattr(args[0], 'message'):
                    message_or_callback = args[0]
                
                # Handle the error
                handled = await _error_handler.handle_telegram_error(e, message_or_callback)
                
                if not handled:
                    # Log unhandled errors
                    if log_error:
                        _error_handler.log_error(e, {'function': func.__name__})
                    
                    # Send default message if not already sent
                    if message_or_callback and not handled:
                        try:
                            if hasattr(message_or_callback, 'answer'):
                                await message_or_callback.answer(default_message)
                            elif hasattr(message_or_callback, 'message') and hasattr(message_or_callback.message, 'answer'):
                                await message_or_callback.message.answer(default_message)
                        except Exception as send_error:
                            logger.error(f"❌ Failed to send error message: {send_error}")
                
                if re_raise:
                    raise e
                
                return None
        return wrapper
    return decorator

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying failed operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            for attempt in range(max_retries + 1):  # +1 for the initial attempt
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"❌ Max retries exceeded for {func.__name__}: {e}")
                        raise e
                    
                    logger.warning(
                        f"🔄 Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                    )
                    
                    # Wait before retry
                    import asyncio
                    await asyncio.sleep(current_delay)
                    
                    # Increase delay for next retry
                    current_delay *= backoff_factor
            
            return None
        return wrapper
    return decorator

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    exceptions: tuple = (Exception,)
):
    """
    Circuit breaker decorator to prevent cascading failures.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time in seconds before attempting recovery
        exceptions: Exceptions that count as failures
    """
    class CircuitBreaker:
        def __init__(self):
            self.failures = 0
            self.last_failure_time = 0
            self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    breaker = CircuitBreaker()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import time
            
            # Check circuit breaker state
            if breaker.state == "OPEN":
                if time.time() - breaker.last_failure_time > recovery_timeout:
                    breaker.state = "HALF_OPEN"
                    logger.info(f"🔶 Circuit half-open for {func.__name__}")
                else:
                    logger.warning(f"🔴 Circuit open for {func.__name__}")
                    raise Exception("Circuit breaker is open")
            
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset circuit if it was half-open
                if breaker.state == "HALF_OPEN":
                    breaker.state = "CLOSED"
                    breaker.failures = 0
                    logger.info(f"✅ Circuit closed for {func.__name__}")
                
                return result
                
            except exceptions as e:
                breaker.failures += 1
                breaker.last_failure_time = time.time()
                
                # Check if we should open the circuit
                if breaker.failures >= failure_threshold:
                    breaker.state = "OPEN"
                    logger.error(f"🔴 Circuit opened for {func.__name__} after {breaker.failures} failures")
                
                raise e
        
        return wrapper
    return decorator

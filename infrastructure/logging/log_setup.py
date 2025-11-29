"""Logging setup and initialization."""
import logging
import logging.config
import os
from typing import Optional

from .log_config import get_logging_config

def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    enable_json_logs: bool = True
) -> None:
    """
    Setup application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to files
        log_dir: Directory for log files
        enable_json_logs: Whether to enable JSON structured logging
    """
    # Create log directory if needed
    if log_to_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"📁 Created log directory: {log_dir}")
    
    # Get logging configuration
    config = get_logging_config(log_level, log_to_file)
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    
    # Log initialization message
    logger.info(f"✅ Logging initialized. Level: {log_level}, File logging: {log_to_file}")
    
    if log_to_file:
        logger.info(f"📁 Log files location: {log_dir}")
        
        # List created log files
        log_files = []
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'baseFilename'):
                log_files.append(handler.baseFilename)
        
        if log_files:
            logger.info(f"📄 Log files: {', '.join(log_files)}")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger with proper configuration.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

class StructuredLogger:
    """Logger for structured logging with context."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def add_context(self, **kwargs):
        """Add context to log messages."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear context."""
        self.context.clear()
    
    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = " ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{message} [{context_str}]"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.add_context(**kwargs)
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.add_context(**kwargs)
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.add_context(**kwargs)
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.add_context(**kwargs)
        self.logger.error(self._format_message(message))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.add_context(**kwargs)
        self.logger.critical(self._format_message(message))
    
    def exception(self, message: str, **kwargs):
        """Log exception with context."""
        self.add_context(**kwargs)
        self.logger.exception(self._format_message(message))

"""Logging configuration."""
import os
import logging
import logging.config
from datetime import datetime
from typing import Dict, Any

def get_logging_config(log_level: str = "INFO", log_to_file: bool = True) -> Dict[str, Any]:
    """Get logging configuration dictionary."""
    
    log_dir = "logs"
    if log_to_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            },
            'json': {
                'format': '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {  # Root logger
                'level': log_level,
                'handlers': ['console']
            }
        }
    }
    
    # Add file handlers if enabled
    if log_to_file:
        # Main application log
        config['handlers']['file_app'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'detailed',
            'filename': os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log"),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
        
        # Error log (only errors and above)
        config['handlers']['file_error'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': os.path.join(log_dir, f"error_{datetime.now().strftime('%Y%m%d')}.log"),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
        
        # JSON log for structured logging
        config['handlers']['file_json'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'json',
            'filename': os.path.join(log_dir, f"structured_{datetime.now().strftime('%Y%m%d')}.log"),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 3,
            'encoding': 'utf8'
        }
        
        # Update root logger to include file handlers
        config['loggers']['']['handlers'].extend(['file_app', 'file_error', 'file_json'])
    
    # Configure specific loggers
    config['loggers']['aiogram'] = {
        'level': 'WARNING',
        'handlers': ['console', 'file_app', 'file_error'] if log_to_file else ['console'],
        'propagate': False
    }
    
    config['loggers']['httpx'] = {
        'level': 'WARNING',
        'handlers': ['console'] if not log_to_file else ['console', 'file_app'],
        'propagate': False
    }
    
    config['loggers']['presentation'] = {
        'level': log_level,
        'handlers': ['console', 'file_app'] if log_to_file else ['console'],
        'propagate': False
    }
    
    config['loggers']['infrastructure'] = {
        'level': log_level,
        'handlers': ['console', 'file_app'] if log_to_file else ['console'],
        'propagate': False
    }
    
    return config

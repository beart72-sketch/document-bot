"""Redis configuration."""
import os

REDIS_CONFIG = {
    'enabled': os.getenv('REDIS_ENABLED', 'false').lower() == 'true',
    'url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
    'default_ttl': int(os.getenv('REDIS_TTL', '3600')),  # 1 hour default
    'connection_pool': {
        'max_connections': 10,
        'retry_on_timeout': True
    }
}

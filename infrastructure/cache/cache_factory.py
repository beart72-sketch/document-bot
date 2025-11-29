"""Cache factory."""
import logging
from infrastructure.config.redis_config import REDIS_CONFIG
from .redis_cache import RedisCache
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

def create_cache():
    """Create cache instance based on configuration."""
    try:
        if REDIS_CONFIG['enabled']:
            logger.info("🚀 Creating Redis cache")
            return RedisCache(
                redis_url=REDIS_CONFIG['url'],
                default_ttl=REDIS_CONFIG['default_ttl']
            )
        else:
            logger.info("🚀 Creating Memory cache")
            return MemoryCache(default_ttl=REDIS_CONFIG['default_ttl'])
    except Exception as e:
        logger.error(f"❌ Failed to create cache: {e}")
        logger.info("🔄 Falling back to Memory cache")
        return MemoryCache()

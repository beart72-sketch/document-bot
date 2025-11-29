"""In-memory cache implementation."""
import time
from typing import Any, Dict, Optional
import logging

from .base_cache import BaseCache

logger = logging.getLogger(__name__)

class MemoryCache(BaseCache):
    """In-memory cache for development and testing."""
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self._storage: Dict[str, Dict[str, Any]] = {}
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        try:
            if key in self._storage:
                data = self._storage[key]
                if data['expires'] > time.time():
                    return data['value']
                else:
                    # Remove expired data
                    del self._storage[key]
            return None
        except Exception as e:
            logger.error(f"❌ Memory cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache."""
        try:
            ttl = ttl or self.default_ttl
            self._storage[key] = {
                'value': value,
                'expires': time.time() + ttl
            }
            logger.debug(f"💾 Memory cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"❌ Memory cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        try:
            if key in self._storage:
                del self._storage[key]
                logger.debug(f"🗑️ Memory cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"❌ Memory cache delete error for key {key}: {e}")
            return False
    
    async def close(self):
        """Clear memory cache."""
        self._storage.clear()
        logger.info("✅ Memory cache cleared")

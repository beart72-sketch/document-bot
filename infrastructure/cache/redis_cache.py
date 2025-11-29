"""Redis cache implementation."""
import json
import logging
from typing import Any, Optional

from .base_cache import BaseCache

logger = logging.getLogger(__name__)

class RedisCache(BaseCache):
    """Redis cache implementation."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 3600):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._client = None
        
    async def _get_client(self):
        """Get Redis client (lazy initialization)."""
        if self._client is None:
            try:
                import redis.asyncio as redis
                self._client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                # Test connection
                await self._client.ping()
                logger.info("✅ Redis connection established")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                raise
        return self._client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            client = await self._get_client()
            data = await client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ Redis get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            client = await self._get_client()
            ttl = ttl or self.default_ttl
            await client.setex(key, ttl, json.dumps(value, default=str))
            logger.debug(f"💾 Redis set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"❌ Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            client = await self._get_client()
            result = await client.delete(key)
            logger.debug(f"🗑️ Redis delete: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"❌ Redis delete error for key {key}: {e}")
            return False
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("✅ Redis connection closed")

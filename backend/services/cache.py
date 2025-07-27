"""Redis cache layer for InsightPulse sentiment analysis results.

Caches inference results by text hash, reducing model load and improving response times.
"""

import json
import hashlib
import logging
from typing import Optional, Dict, Any
import redis
from redis.exceptions import RedisError
from core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Constants
CACHE_KEY_PREFIX = "sent:"  # Optional: move to settings if needed
DEFAULT_TTL = 3600  # Seconds, or set in settings

# Initialize Redis client (thread-safe for sync use)
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
)

def _cache_key(text: str) -> str:
    """Generate a deterministic, unique Redis key for the given text."""
    h = hashlib.sha256(text.strip().encode()).hexdigest()
    return f"{CACHE_KEY_PREFIX}{h}"

def get(text: str) -> Optional[Dict[str, Any]]:
    """Get cached sentiment analysis result for a text.
    
    Args:
        text: Input string to look up in cache.
    
    Returns:
        dict: Cached result, or None if not found or on error.
    """
    key = _cache_key(text)
    try:
        data = redis_client.get(key)
        if data is not None:
            logger.debug("Cache hit for key: %s", key)
            return json.loads(data)
    except (RedisError, json.JSONDecodeError) as e:
        logger.error("Cache get error for key %s: %s", key, e, exc_info=True)
    return None

def set(text: str, payload: Dict[str, Any], ttl: int = DEFAULT_TTL) -> bool:
    """Cache a sentiment analysis result.
    
    Args:
        text: Input string to cache under.
        payload: Result dictionary to cache.
        ttl: Cache lifetime in seconds.
    
    Returns:
        bool: True if cached successfully, False on error.
    """
    key = _cache_key(text)
    try:
        redis_client.setex(key, ttl, json.dumps(payload))
        logger.debug("Cache set for key: %s", key)
        return True
    except (RedisError, TypeError) as e:
        logger.error("Cache set error for key %s: %s", key, e, exc_info=True)
        return False

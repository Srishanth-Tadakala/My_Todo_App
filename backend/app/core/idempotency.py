"""
Idempotency Handler
Provides in-memory caching of responses for requests containing an Idempotency-Key header.
"""

import time
from typing import Any, Dict, Optional, Tuple


class IdempotencyCache:
    """Stores response payloads keyed by idempotency key with TTL."""

    def __init__(self, ttl_seconds: int = 86400):  # 24 hours
        self.ttl_seconds = ttl_seconds
        # key -> (expiry_timestamp, status_code, payload)
        self._cache: Dict[str, Tuple[float, int, Any]] = {}

    def get(self, key: str) -> Optional[Tuple[int, Any]]:
        now = time.time()
        if key in self._cache:
            expiry, status_code, payload = self._cache[key]
            if now < expiry:
                return status_code, payload
            del self._cache[key]
        return None

    def set(self, key: str, status_code: int, payload: Any):
        expiry = time.time() + self.ttl_seconds
        self._cache[key] = (expiry, status_code, payload)

    def cleanup(self):
        now = time.time()
        expired_keys = [k for k, (exp, _, _) in self._cache.items() if now >= exp]
        for k in expired_keys:
            del self._cache[k]


idempotency_cache = IdempotencyCache()

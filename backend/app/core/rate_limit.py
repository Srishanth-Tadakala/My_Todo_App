"""
In-Memory Rate Limiting
Provides simple token-bucket / sliding window rate limiting for sensitive endpoints.
"""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request
from app.core.exceptions import RateLimitException


class InMemoryRateLimiter:
    """Simple in-memory sliding-window rate limiter."""

    def __init__(self, requests_limit: int = 60, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = defaultdict(list)

    def check(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Clean older entries
        self.history[key] = [t for t in self.history[key] if t > cutoff]

        if len(self.history[key]) >= self.requests_limit:
            return False

        self.history[key].append(now)
        return True


# Global rate limiter instances for different routes
auth_limiter = InMemoryRateLimiter(requests_limit=15, window_seconds=60)
search_limiter = InMemoryRateLimiter(requests_limit=30, window_seconds=60)
notification_limiter = InMemoryRateLimiter(requests_limit=20, window_seconds=60)


async def rate_limit_auth(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not auth_limiter.check(f"auth:{client_ip}"):
        raise RateLimitException("Too many auth attempts. Please wait a minute.")


async def rate_limit_search(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not search_limiter.check(f"search:{client_ip}"):
        raise RateLimitException("Search rate limit exceeded. Please wait.")

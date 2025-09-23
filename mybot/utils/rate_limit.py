"""In-memory rate limiting helpers."""

from __future__ import annotations

import time
from collections import deque
from typing import Deque, Dict, Tuple


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""


class RateLimiter:
    def __init__(self, *, limit: int, window: float):
        self.limit = limit
        self.window = window
        self._hits: Dict[Tuple[str, int], Deque[float]] = {}

    def hit(self, bucket: str, key: int) -> None:
        now = time.monotonic()
        queue = self._hits.setdefault((bucket, key), deque())
        while queue and now - queue[0] > self.window:
            queue.popleft()
        if len(queue) >= self.limit:
            raise RateLimitExceeded(f"Rate limit exceeded for {bucket}:{key}")
        queue.append(now)

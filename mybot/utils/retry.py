"""Retry helpers with exponential backoff."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


async def retry(  # pragma: no cover - simple wrapper
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
) -> T:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await operation()
        except Exception as exc:  # pragma: no cover - upstream errors
            last_error = exc
            await asyncio.sleep(base_delay * (2**attempt))
    assert last_error is not None
    raise last_error

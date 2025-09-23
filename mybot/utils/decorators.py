"""Decorators for handler instrumentation."""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar

from pyrogram.errors import RPCError

LOGGER = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def log_errors(func: F) -> F:
    """Log exceptions raised by handlers and prevent crashes."""

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            try:
                return await func(*args, **kwargs)
            except RPCError as exc:  # pragma: no cover - network errors
                LOGGER.warning("Telegram RPC error in %s: %s", func.__name__, exc)
            except Exception:  # pragma: no cover - defensive logging
                LOGGER.exception("Unhandled exception in handler %s", func.__name__)

        return wrapper  # type: ignore[misc]

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except Exception:  # pragma: no cover - defensive logging
            LOGGER.exception("Unhandled exception in handler %s", func.__name__)

    return sync_wrapper  # type: ignore[misc]

import functools
import logging

LOGGER = logging.getLogger(__name__)


def log_errors(func):
    """Decorator to log exceptions and always reply with an error message."""

    @functools.wraps(func)
    async def wrapper(client, *args, **kwargs):
        LOGGER.debug("Handler %s triggered", func.__name__)
        try:
            return await func(client, *args, **kwargs)
        except Exception as exc:  # pragma: no cover - runtime safety
            LOGGER.exception("Unhandled exception in %s", func.__name__)
            # Try to reply politely using context information
            for arg in args:
                target = getattr(arg, "message", arg)
                if hasattr(target, "reply_text"):
                    try:
                        await target.reply_text(
                            "\u26a0\ufe0f An unexpected error occurred. Please try again later."
                        )
                    except Exception:
                        pass
                    break
            return None

    return wrapper

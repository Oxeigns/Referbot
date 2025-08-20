"""Dispatcher handler registration utilities.

This module provides a minimal stub for Aiogram-based projects so that
``mybot.main`` can import ``register_handlers``.  In the original Pyrogram
implementation, handlers were loaded via the plugin system.  For Aiogram the
pattern is typically to register routers or handlers explicitly; here we simply
expose a function that does nothing to keep the example lightweight.
"""

from aiogram import Dispatcher


def register_handlers(dp: Dispatcher, banner_url: str | None = None) -> None:
    """Register bot handlers with the dispatcher.

    Parameters
    ----------
    dp: Dispatcher
        The Aiogram dispatcher instance.
    banner_url: Optional[str]
        URL of a banner image to be used by handlers.  Included for API
        compatibility with the user request; currently unused.
    """

    # In a full application you would import routers/modules here and attach
    # them to ``dp``.  For this repository no handlers are required, so the
    # function is intentionally empty.
    return None

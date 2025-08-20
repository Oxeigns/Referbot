"""Webhook utilities for running or removing the bot's webhook."""

from aiogram import Bot, Dispatcher
from loguru import logger


async def run_webhook(bot: Bot, dp: Dispatcher) -> None:
    """Start the webhook server.

    The real webhook implementation is outside the scope of this repository.
    This placeholder logs the intent so that the function can be safely called
    without side effects during tests.
    """

    logger.warning("Webhook mode requested but not implemented. Running polling instead.")


async def delete_webhook(bot: Bot) -> None:
    """Remove any existing webhook from Telegram servers."""

    try:
        await bot.delete_webhook()
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Failed to delete webhook: %s", exc)

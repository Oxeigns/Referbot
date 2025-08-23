"""Entry point for running the Telegram bot using Aiogram.

This file mirrors the structure suggested by the user request.  It sets up
logging, initialises the bot and dispatcher, and either starts polling or runs
in webhook mode depending on configuration.
"""

import asyncio
import logging

from pyrogram import Bot, Dispatcher
from pyrogram.contrib.fsm_storage.memory import MemoryStorage
from pyrogram.utils.executor import start_polling
from loguru import logger

from mybot.config import load_config
from mybot.handlers import register_handlers
from mybot.webhooks.handler import run_webhook, delete_webhook
from mybot.database.mongo import init_indexes


def setup_logging() -> None:
    """Configure standard logging and loguru."""

    logging.basicConfig(level=logging.INFO)
    logger.add("bot.log", rotation="10 MB")


def main() -> None:
    cfg = load_config()
    setup_logging()

    bot = Bot(token=cfg.BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers(dp, banner_url=cfg.BANNER_URL)

    async def on_startup(dispatcher: Dispatcher) -> None:
        await init_indexes()
        if not cfg.USE_WEBHOOK:
            await delete_webhook(bot)
        logger.info("🚀 Bot started (webhook=%s)", cfg.USE_WEBHOOK)

    async def on_shutdown(dispatcher: Dispatcher) -> None:
        await bot.session.close()
        logger.info("🛑 Bot shutdown complete")

    if cfg.USE_WEBHOOK:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_webhook(bot, dp))
    else:
        start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )


if __name__ == "__main__":  # pragma: no cover - manual execution guard
    main()

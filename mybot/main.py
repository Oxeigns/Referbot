"""Main entry point for the Refer & Earn Telegram bot."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
import asyncio

from pyrogram import Client, idle

from mybot import config
from mybot.database import init_db
from mybot.database.mongo import mongo_client


# -------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.DEBUG),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "debug.log", encoding="utf-8"),
    ],
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pymongo").setLevel(logging.WARNING)

# -------------------------------------------------------------
# Pyrogram Client
# -------------------------------------------------------------
app = Client(
    "refer_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="mybot.plugins"),
)


async def main() -> None:
    """Initialize services and run the bot until stopped."""
    LOGGER.info("📜 Initializing database...")
    await init_db()

    LOGGER.info("Bot starting...")
    # IMPORTANT: Start the bot before idle
    await app.start()

    LOGGER.info("Bot started. Listening for updates.")
    try:
        await idle()
    finally:
        await app.stop()
        mongo_client.close()
        LOGGER.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:  # pragma: no cover - runtime errors
        LOGGER.exception("Bot stopped due to error: %s", exc)

"""Main entry point for the Refer & Earn Telegram bot."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from pyrogram import Client

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
    # Load all modules inside ``mybot/plugins`` so handlers register automatically
    plugins={"root": "mybot/plugins"},
)



async def on_startup() -> None:
    """Prepare services that should run after the client starts."""
    LOGGER.info("📜 Initializing database...")
    await init_db()
    LOGGER.info("Bot started. Listening for updates.")


if __name__ == "__main__":
    try:
        # ``app.run`` starts the client, runs the coroutine, handles ``idle``
        # internally, and stops the client on exit.
        app.run(on_startup())
    except Exception as exc:  # pragma: no cover - runtime errors
        LOGGER.exception("Bot stopped due to error: %s", exc)
    finally:
        mongo_client.close()
        LOGGER.info("Bot stopped.")

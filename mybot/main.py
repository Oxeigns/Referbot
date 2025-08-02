"""Main entry point for the Refer & Earn Telegram bot."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

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
)


# -------------------------------------------------------------
# Global update logger
# -------------------------------------------------------------
@app.on_message(group=-1)
async def log_updates(_, message):
    """Log every incoming message before other handlers."""
    user_id = getattr(message.from_user, "id", "unknown")
    text = message.text or message.caption or ""
    LOGGER.info("Update from %s: %s", user_id, text)


@app.on_callback_query(group=-1)
async def log_callbacks(_, callback_query):
    """Log callback queries as they arrive."""
    user_id = getattr(callback_query.from_user, "id", "unknown")
    LOGGER.info("Callback from %s: %s", user_id, callback_query.data)


# -------------------------------------------------------------
# Plugin loading
# -------------------------------------------------------------
PLUGIN_ROOT = Path(__file__).resolve().parent / "plugins"
LOGGER.info(">>> LOADING PLUGINS...")
app.load_plugins(str(PLUGIN_ROOT))
LOGGER.info(">>> PLUGINS LOADED SUCCESSFULLY")


async def on_startup() -> None:
    """Prepare services that should run after the client starts."""
    LOGGER.info(">>> BOT CONNECTED TO TELEGRAM")
    LOGGER.info("📜 Initializing database...")
    try:
        await init_db()
    except Exception as exc:  # pragma: no cover - runtime errors
        LOGGER.exception("Database initialization failed: %s", exc)
    LOGGER.info("Bot started. Listening for updates.")
    await idle()


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

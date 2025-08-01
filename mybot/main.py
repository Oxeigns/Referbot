"""Main entrypoint for the Refer & Earn Telegram Bot (Polling only)."""

import logging
import sys
from importlib import import_module
from pathlib import Path

from pyrogram import Client

from mybot import config
from mybot.database import init_db

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

# -------------------------------------------------------------
# Pyrogram Client
# -------------------------------------------------------------
app = Client(
    "refer_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)


def load_plugins() -> None:
    """Dynamically import all plugin modules and log them."""
    plugins_path = Path(__file__).parent / "plugins"
    for file in plugins_path.glob("*.py"):
        if file.name.startswith("__"):
            continue
        module_name = f"mybot.plugins.{file.stem}"
        try:
            import_module(module_name)
            LOGGER.info("Plugin loaded: %s", module_name)
        except Exception as exc:  # pragma: no cover - import errors
            LOGGER.exception("Failed to load plugin %s: %s", module_name, exc)

# -------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------
async def start_bot() -> None:
    LOGGER.info("\U0001F4DC Initializing database...")
    await init_db()

    LOGGER.info("\U0001F527 Loading plugins...")
    load_plugins()


if __name__ == "__main__":
    try:
        app.run(start_bot())
    except Exception as exc:  # pragma: no cover - runtime errors
        LOGGER.exception("Bot stopped due to error: %s", exc)


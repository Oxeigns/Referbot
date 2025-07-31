"""Main entrypoint for the Refer & Earn Telegram Bot (Polling only)."""

import asyncio
import logging
import sys
from pathlib import Path
from glob import glob
import importlib

from pyrogram import Client, filters, idle
from mybot import config
from mybot.database import init_db

# -------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "debug.log", encoding="utf-8"),
    ],
)
error_handler = logging.FileHandler(LOG_DIR / "error.log", encoding="utf-8")
error_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(error_handler)

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

# -------------------------------------------------------------
# Dynamic plugin loader
# -------------------------------------------------------------
def load_plugins():
    """Import all Python modules inside mybot/plugins/."""
    plugin_paths = glob("mybot/plugins/*.py")
    loaded = 0
    for path in plugin_paths:
        if path.endswith("__init__.py"):
            continue
        module = path.replace("/", ".").replace("\\", ".")[:-3]
        importlib.import_module(module)
        loaded += 1
    LOGGER.info(f"✅ Loaded {loaded} plugins.")
    return loaded

# -------------------------------------------------------------
# Simple admin command for testing
# -------------------------------------------------------------
@app.on_message(filters.command("ping") & filters.user(config.OWNER_ID))
async def ping(_, message):
    await message.reply_text("Pong!")

# -------------------------------------------------------------
# Polling startup
# -------------------------------------------------------------
async def main():
    # Initialize DB
    LOGGER.info("📚 Initializing database...")
    await init_db()
    LOGGER.info("✅ Database ready")

    # Load plugins
    load_plugins()

    LOGGER.info("🚀 Starting Refer & Earn Bot in polling mode...")
    async with app:
        LOGGER.info("✅ Bot is ready to receive updates.")
        await idle()
    LOGGER.info("Bot stopped cleanly.")

# -------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("🔌 Interrupted, exiting...")

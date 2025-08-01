"""Main entrypoint for the Refer & Earn Telegram Bot (Polling only)."""

import logging
import sys
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
    plugins=dict(root="mybot/plugins"),
)

# -------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------
if __name__ == "__main__":
    LOGGER.info("📚 Initializing database...")
    # Initialize MongoDB before bot starts
    import asyncio
    asyncio.run(init_db())

    LOGGER.info("🚀 Starting Refer & Earn Bot in polling mode...")
    # This single line starts the client, loads plugins, and processes updates
    app.run()

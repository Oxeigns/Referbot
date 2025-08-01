"""Main entrypoint for the Refer & Earn Telegram Bot (Polling only)."""

import asyncio
import logging
import sys
from pathlib import Path

from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
import httpx
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
    plugins=dict(root="mybot/plugins"),
)


# -------------------------------------------------------------
# Simple admin command for testing
# -------------------------------------------------------------
@app.on_message(filters.command("ping") & filters.user(config.OWNER_ID))
async def ping(_, message):
    await message.reply_text("Pong!")

# -------------------------------------------------------------
# Polling startup
# -------------------------------------------------------------
async def start_client_with_retry():
    """Start the Pyrogram client handling FloodWait automatically."""
    while True:
        try:
            await app.start()
            LOGGER.info("✅ Client started")
            break
        except FloodWait as e:
            wait_time = int(e.value)
            LOGGER.warning(
                "⚠️ Received FloodWait for %d seconds while starting. Waiting...",
                wait_time,
            )
            await asyncio.sleep(wait_time)


async def delete_webhook(drop_pending_updates: bool = True) -> None:
    """Delete existing webhook via Bot API."""
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/deleteWebhook"
    params = {"drop_pending_updates": str(drop_pending_updates).lower()}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, params=params)
        except Exception as exc:
            LOGGER.warning("Failed to delete webhook: %s", exc)


async def main():
    # Initialize DB
    LOGGER.info("📚 Initializing database...")
    await init_db()
    LOGGER.info("✅ Database ready")

    LOGGER.info("🚀 Starting Refer & Earn Bot in polling mode...")

    # Load Pyrogram plugins from the plugins folder
    app.load_plugins()

    await start_client_with_retry()
    try:
        # Ensure no leftover webhook is set
        await delete_webhook(drop_pending_updates=True)
        LOGGER.info("✅ Bot is ready to receive updates.")
        await idle()
    finally:
        await app.stop()
    LOGGER.info("Bot stopped cleanly.")

# -------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("🔌 Interrupted, exiting...")

import asyncio
from pyrogram import Client
from pyrogram import filters
from glob import glob
import importlib
import logging

from mybot import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client(
    "refer-bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

# dynamically load plugins
for path in glob("mybot/plugins/*.py"):
    name = path.replace('/', '.').rstrip(".py")
    importlib.import_module(name)

@app.on_message(filters.command("ping") & filters.user(config.OWNER_ID))
async def ping(_, message):
    await message.reply_text("Pong!")

if __name__ == "__main__":
    logger.info("Bot Started")
    app.run()

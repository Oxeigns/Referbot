from pyrogram import Client, filters
import logging

from mybot.utils.decorators import log_errors

LOGGER = logging.getLogger(__name__)
LOGGER.info("Plugin loaded: %s", __name__)

@Client.on_message(filters.command("pingtest"))
@log_errors
async def pingtest_cmd(_, message):
    LOGGER.info("pingtest command from %s", message.from_user.id)
    await message.reply_text("Pong! (test plugin)")


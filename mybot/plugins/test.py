from pyrogram import Client, filters
import logging

from mybot.utils.decorators import log_errors

LOGGER = logging.getLogger(__name__)

@Client.on_message(filters.command("ping"))
@log_errors
async def ping_test(_, message):
    LOGGER.info("ping command from %s", message.from_user.id)
    await message.reply_text("Pong! (test plugin)")


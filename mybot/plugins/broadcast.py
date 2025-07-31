from pyrogram import Client, filters
from mybot.database.mongo import users_col
from mybot import config
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def broadcast_cmd(client, message):
    try:
        if len(message.command) < 2 and not message.reply_to_message:
            return await message.reply_text("Usage: /broadcast <message>")
        text = (
            message.text.split(None, 1)[1]
            if len(message.command) >= 2
            else message.reply_to_message.text
        )
        sent = 0
        failed = 0
        async for user in users_col.find({}, {"_id": 1}):
            try:
                await client.send_message(user["_id"], text)
                sent += 1
            except Exception as e:
                logger.error("Broadcast to %s failed: %s", user["_id"], e)
                failed += 1
        await message.reply_text(f"Broadcast completed. Sent: {sent}, Failed: {failed}")
    except Exception as e:
        logger.exception("broadcast_cmd failed: %s", e)

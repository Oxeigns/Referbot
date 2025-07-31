from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from mybot.database.mongo import users_col
from mybot import config


@Client.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def broadcast_cmd(client, message):
    """Broadcast a message to all users.

    Usage: Reply to a message with /broadcast or use /broadcast <text>.
    """
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("Reply to a message or give text to broadcast.")

    sent = 0
    async for user in users_col.find():
        try:
            await client.send_message(user["_id"], text, parse_mode=ParseMode.HTML)
            sent += 1
        except Exception:
            continue
    await message.reply_text(f"Broadcast sent to {sent} users.")

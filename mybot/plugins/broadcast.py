from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import logging
import html

from mybot.database.mongo import users_col
from mybot import config
from mybot.utils.decorators import log_errors

LOGGER = logging.getLogger(__name__)
LOGGER.info("Plugin loaded: %s", __name__)


@Client.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
@log_errors
async def broadcast_cmd(client, message):
    LOGGER.info("Broadcast triggered by %s", message.from_user.id)
    """
    Broadcast a message to all users.

    Usage:
      - Reply to a message with /broadcast
      - Or use: /broadcast <text>
    """
    # Determine the broadcast text
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text(
            "⚠️ <b>Usage:</b>\n"
            "Reply with /broadcast or send:\n"
            "<code>/broadcast Your text here</code>",
            parse_mode=ParseMode.HTML,
        )

    if not text:
        return await message.reply_text(
            "❌ No text to broadcast.",
            parse_mode=ParseMode.HTML,
        )

    # Escape HTML to avoid errors if text contains < or >
    safe_text = html.escape(text)

    sent = 0
    failed = 0

    # Iterate over all users in DB
    try:
        cursor = users_col.find({}, {"_id": 1})
        async for user in cursor:
            user_id = user["_id"]
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=safe_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                sent += 1
            except Exception:
                failed += 1
                continue
    except Exception as e:
        LOGGER.exception("DB error during broadcast: %s", e)

    await message.reply_text(
        f"📢 Broadcast completed.\n\n"
        f"✅ Delivered to: <b>{sent}</b> users\n"
        f"❌ Failed: <b>{failed}</b> users",
        parse_mode=ParseMode.HTML,
    )


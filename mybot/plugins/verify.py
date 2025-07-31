from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot import config


@Client.on_callback_query(filters.regex("^verify$"))
async def verify_cb(client, callback_query):
    user_id = callback_query.from_user.id
    missing = []
    for ch in config.CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in ("kicked", "left"):
                missing.append(ch)
        except Exception:
            missing.append(ch)
    if missing:
        text = "Please join all channels and try again:\n" + "\n".join(f"@{ch}" for ch in missing)
        await callback_query.message.reply_text(text, quote=True)
    else:
        await callback_query.message.reply_text("Verification successful!", quote=True)
    await callback_query.answer()

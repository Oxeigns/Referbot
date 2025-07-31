from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from mybot import config


@Client.on_callback_query(filters.regex("^verify$"))
async def verify_cb(client, callback_query):
    """Verify if the user has joined all required channels."""
    user_id = callback_query.from_user.id
    missing = []

    # Check membership for each required channel
    for ch in config.CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in ("kicked", "left"):
                missing.append(ch)
        except Exception:
            # If bot can't access the channel or user not found
            missing.append(ch)

    if missing:
        # Show channels that still need to be joined
        missing_list = "\n".join(f"• @{ch}" for ch in missing)
        text = (
            "❌ <b>Verification Failed</b>\n\n"
            "Please join all the required channels before verifying again:\n\n"
            f"{missing_list}"
        )
        await callback_query.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            quote=True
        )
    else:
        await callback_query.message.reply_text(
            "✅ <b>Verification Successful!</b>\n\n"
            "You have joined all the required channels.",
            parse_mode=ParseMode.HTML,
            quote=True
        )

    await callback_query.answer()

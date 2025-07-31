from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from mybot.database.mongo import settings_col


@Client.on_callback_query(filters.regex("^verify$"))
async def verify_cb(client, callback_query):
    """Verify if the user has joined all required channels."""
    user_id = callback_query.from_user.id
    missing = []

    # Fetch channel buttons from DB
    doc = await settings_col.find_one({"_id": "channels"})
    buttons = doc.get("buttons", {}) if doc else {}

    if not buttons:
        await callback_query.message.reply_text(
            "✅ <b>Verification Successful!</b>\n\nNo channels configured.",
            parse_mode=ParseMode.HTML,
            quote=True,
        )
        await callback_query.answer()
        return

    # Check membership for each public channel
    for link in buttons.values():
        if "/+" in link or "joinchat" in link:
            # Skip invite links
            continue
        if "t.me/" in link:
            username = link.split("t.me/")[1].split("?", 1)[0].strip("/")
        else:
            continue
        try:
            member = await client.get_chat_member(username, user_id)
            if member.status in {ChatMemberStatus.BANNED, ChatMemberStatus.LEFT}:
                missing.append(username)
        except Exception:
            missing.append(username)

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
            quote=True,
        )
    else:
        await callback_query.message.reply_text(
            "✅ <b>Verification Successful!</b>\n\n"
            "You have joined all the required channels.",
            parse_mode=ParseMode.HTML,
            quote=True,
        )

    await callback_query.answer()

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot.database.mongo import users_col
from mybot import config
from mybot.button import SUPPORT_URL
from datetime import datetime


# Admin Panel callback button
@Client.on_callback_query(filters.regex("^admin$") & filters.user(config.OWNER_ID))
async def admin_panel(client, callback_query):
    text = (
        "🛠 <b>Admin Panel</b>\n\n"
        "Use the following commands:\n\n"
        "• <code>/points &lt;user_id&gt;</code> – Show user points\n"
        "• <code>/approve &lt;user_id&gt;</code> – Approve pending withdrawal\n"
        "• <code>/reject &lt;user_id&gt;</code> – Reject withdrawal request"
    )

    await callback_query.message.reply_text(
        text, quote=True, disable_web_page_preview=True
    )
    await callback_query.answer("Admin panel opened!")


# Show user points
@Client.on_message(filters.command("points") & filters.user(config.OWNER_ID))
async def points_cmd(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/points &lt;user_id&gt;</code>", parse_mode="html"
        )

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID format.", parse_mode="html")

    user = await users_col.find_one({"_id": uid})
    if not user:
        return await message.reply_text(
            f"❌ No data found for user <code>{uid}</code>", parse_mode="html"
        )

    points = user.get("points", 0)
    await message.reply_text(
        f"📊 <b>User:</b> <code>{uid}</code>\n" f"💎 <b>Points:</b> {points}",
        parse_mode="html",
    )


# Approve withdrawal
@Client.on_message(filters.command("approve") & filters.user(config.OWNER_ID))
async def approve_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/approve &lt;user_id&gt;</code>", parse_mode="html"
        )

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID format.", parse_mode="html")

    user = await users_col.find_one({"_id": uid})
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text(
            "❌ No pending withdrawal request for this user.", parse_mode="html"
        )

    amount = user.get("pending_withdrawal")
    current_points = user.get("points", 0)

    if current_points < amount:
        return await message.reply_text(
            "⚠️ Insufficient points in user's account.", parse_mode="html"
        )

    await users_col.update_one(
        {"_id": uid},
        {"$inc": {"points": -amount}, "$unset": {"pending_withdrawal": ""}},
    )

    await message.reply_text(
        f"✅ Approved withdrawal of <b>{amount}</b> points for user <code>{uid}</code>",
        parse_mode="html",
    )

    # Log withdrawal in LOG_GROUP with a support button
    if config.LOG_GROUP:
        user_obj = await client.get_users(uid)
        log_text = (
            "💸 <b>Withdrawal Completed</b>\n\n"
            f"👤 <b>User:</b> {user_obj.mention}\n"
            f"🆔 <code>{uid}</code>\n"
            f"💰 <b>Amount:</b> {amount}\n"
            f"📅 <b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💬 Support", url=SUPPORT_URL)]]
        )
        await client.send_message(
            chat_id=int(config.LOG_GROUP),
            text=log_text,
            reply_markup=keyboard,
            parse_mode="html",
        )


# Reject withdrawal
@Client.on_message(filters.command("reject") & filters.user(config.OWNER_ID))
async def reject_cmd(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/reject &lt;user_id&gt;</code>", parse_mode="html"
        )

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID format.", parse_mode="html")

    user = await users_col.find_one({"_id": uid})
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text(
            "❌ No pending withdrawal request for this user.", parse_mode="html"
        )

    await users_col.update_one({"_id": uid}, {"$unset": {"pending_withdrawal": ""}})
    await message.reply_text(
        f"❌ Rejected withdrawal request from user <code>{uid}</code>",
        parse_mode="html",
    )

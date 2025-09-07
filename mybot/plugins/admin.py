from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from datetime import datetime
import logging

from mybot.database.mongo import users_col
from mybot import config
from mybot.button import SUPPORT_URL
from mybot.utils.decorators import log_errors

LOGGER = logging.getLogger(__name__)
LOGGER.info("Plugin loaded: %s", __name__)


# Admin Panel callback button
@Client.on_callback_query(filters.regex("^admin$") & filters.user(config.OWNER_ID))
@log_errors
async def admin_panel(client, callback_query):
    LOGGER.info("Admin panel opened by %s", callback_query.from_user.id)
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
@log_errors
async def points_cmd(_, message):
    LOGGER.info("/points used by %s", message.from_user.id)
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/points &lt;user_id&gt;</code>",
            parse_mode=ParseMode.HTML,
        )

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text(
            "❌ Invalid user ID format.",
            parse_mode=ParseMode.HTML,
        )

    try:
        user = await users_col.find_one({"_id": uid})
    except Exception as e:
        LOGGER.exception("DB error in points_cmd: %s", e)
        user = None
    if not user:
        return await message.reply_text(
            f"❌ No data found for user <code>{uid}</code>",
            parse_mode=ParseMode.HTML,
        )

    points = user.get("points", 0)
    await message.reply_text(
        f"📊 <b>User:</b> <code>{uid}</code>\n" f"💎 <b>Points:</b> {points}",
        parse_mode=ParseMode.HTML,
    )


# Approve withdrawal
@Client.on_message(filters.command("approve") & filters.user(config.OWNER_ID))
@log_errors
async def approve_cmd(client, message):
    LOGGER.info("/approve used by %s", message.from_user.id)
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/approve &lt;user_id&gt;</code>",
            parse_mode=ParseMode.HTML,
        )

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text(
            "❌ Invalid user ID format.",
            parse_mode=ParseMode.HTML,
        )

    try:
        user = await users_col.find_one({"_id": uid})
    except Exception as e:
        LOGGER.exception("DB error in approve_cmd: %s", e)
        user = None
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text(
            "❌ No pending withdrawal request for this user.",
            parse_mode=ParseMode.HTML,
        )

    amount = user.get("pending_withdrawal")
    current_points = user.get("points", 0)

    if current_points < amount:
        return await message.reply_text(
            "⚠️ Insufficient points in user's account.",
            parse_mode=ParseMode.HTML,
        )

    try:
        await users_col.update_one(
            {"_id": uid},
            {"$inc": {"points": -amount}, "$unset": {"pending_withdrawal": ""}},
        )
    except Exception as e:
        LOGGER.exception("DB update failed in approve_cmd: %s", e)

    await message.reply_text(
        f"✅ Approved withdrawal of <b>{amount}</b> points for user <code>{uid}</code>",
        parse_mode=ParseMode.HTML,
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
            parse_mode=ParseMode.HTML,
        )


# Reject withdrawal
@Client.on_message(filters.command("reject") & filters.user(config.OWNER_ID))
@log_errors
async def reject_cmd(_, message):
    LOGGER.info("/reject used by %s", message.from_user.id)
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/reject &lt;user_id&gt;</code>",
            parse_mode=ParseMode.HTML,
        )

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text(
            "❌ Invalid user ID format.",
            parse_mode=ParseMode.HTML,
        )

    try:
        user = await users_col.find_one({"_id": uid})
    except Exception as e:
        LOGGER.exception("DB error in reject_cmd: %s", e)
        user = None
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text(
            "❌ No pending withdrawal request for this user.",
            parse_mode=ParseMode.HTML,
        )

    try:
        await users_col.update_one({"_id": uid}, {"$unset": {"pending_withdrawal": ""}})
    except Exception as e:
        LOGGER.exception("DB update failed in reject_cmd: %s", e)
    await message.reply_text(
        f"❌ Rejected withdrawal request from user <code>{uid}</code>",
        parse_mode=ParseMode.HTML,
    )


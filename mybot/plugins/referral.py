from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import logging

from mybot.database.mongo import users_col
from mybot import config
from mybot.utils.decorators import log_errors

LOGGER = logging.getLogger(__name__)


# Callback: Show referral link and points
@Client.on_callback_query(filters.regex("^referral$"))
@log_errors
async def referral_cb(client, callback_query):
    LOGGER.info("referral callback from %s", callback_query.from_user.id)
    user = callback_query.from_user
    bot = await client.get_me()

    link = f"https://t.me/{bot.username}?start={user.id}"
    points = 0
    try:
        data = await users_col.find_one({"_id": user.id}) or {}
        points = data.get("points", 0)
    except Exception as e:
        LOGGER.exception("DB error in referral_cb: %s", e)

    text = (
        "🎯 <b>Refer & Earn</b>\n\n"
        f"Invite your friends using this link:\n\n<code>{link}</code>\n\n"
        f"💎 <b>Your Points:</b> {points}"
    )

    await callback_query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 Share Link", url=link)]]
        ),
        parse_mode=ParseMode.HTML,
        quote=True,
        disable_web_page_preview=True
    )
    await callback_query.answer("Referral link shown!")


# Callback: Request withdrawal
@Client.on_callback_query(filters.regex("^withdraw$"))
@log_errors
async def withdraw_cb(client, callback_query):
    LOGGER.info("withdraw callback from %s", callback_query.from_user.id)
    user_id = callback_query.from_user.id
    user = None
    try:
        user = await users_col.find_one({"_id": user_id})
    except Exception as e:
        LOGGER.exception("DB lookup failed in withdraw_cb: %s", e)

    # Check minimum points
    if not user or user.get("points", 0) < config.MIN_WITHDRAW:
        await callback_query.message.reply_text(
            f"⚠️ You need at least <b>{config.MIN_WITHDRAW}</b> points to request a withdrawal.",
            parse_mode=ParseMode.HTML,
            quote=True
        )
        return await callback_query.answer()

    # Check if a request already exists
    if user.get("pending_withdrawal"):
        await callback_query.message.reply_text(
            "⏳ You already have a pending withdrawal request.",
            quote=True
        )
        return await callback_query.answer()

    # Set pending withdrawal equal to current points
    try:
        await users_col.update_one(
            {"_id": user_id},
            {"$set": {"pending_withdrawal": user.get("points", 0)}}
        )
    except Exception as e:
        LOGGER.exception("Failed to update withdrawal: %s", e)

    await callback_query.message.reply_text(
        "✅ Your withdrawal request has been submitted. An admin will review it soon.",
        quote=True
    )
    await callback_query.answer("Withdrawal request sent!")


# Callback: Show my points
@Client.on_callback_query(filters.regex("^mypoints$"))
@log_errors
async def mypoints_cb(client, callback_query):
    LOGGER.info("mypoints callback from %s", callback_query.from_user.id)
    points = 0
    try:
        data = await users_col.find_one({"_id": callback_query.from_user.id}) or {}
        points = data.get("points", 0)
    except Exception as e:
        LOGGER.exception("DB error in mypoints_cb: %s", e)

    await callback_query.message.reply_text(
        f"💎 You currently have <b>{points}</b> points.",
        parse_mode=ParseMode.HTML,
        quote=True
    )
    await callback_query.answer("Points displayed!")


# Callback: Show top 10 users by points
@Client.on_callback_query(filters.regex("^top$"))
@log_errors
async def top_cb(client, callback_query):
    LOGGER.info("top users callback from %s", callback_query.from_user.id)
    text = "🏆 <b>Top 10 Users</b>\n\n"
    try:
        top_users_cursor = users_col.find().sort("points", -1).limit(10)
    except Exception as e:
        LOGGER.exception("DB error getting top users: %s", e)
        top_users_cursor = []
    rank = 1

    async for user in top_users_cursor:
        text += f"{rank}. <code>{user['_id']}</code> — {user.get('points', 0)} points\n"
        rank += 1

    if rank == 1:
        text = "No users found."

    await callback_query.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        quote=True,
        disable_web_page_preview=True
    )
    await callback_query.answer("Leaderboard displayed!")


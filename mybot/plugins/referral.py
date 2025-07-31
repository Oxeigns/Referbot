from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot.database.mongo import users_col
from mybot import config
import logging

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^referral$"))
async def referral_cb(client, callback_query):
    try:
        user = callback_query.from_user
        bot = await client.get_me()
        link = f"https://t.me/{bot.username}?start={user.id}"
        data = await users_col.find_one({"_id": user.id}) or {}
        points = data.get("points", 0)
        await callback_query.message.reply_text(
            f"Invite your friends using the link below:\n{link}\n\nYou have <b>{points}</b> points.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share Link", url=link)]]),
            quote=True,
        )
        await callback_query.answer()
    except Exception as e:
        logger.exception("referral_cb failed: %s", e)


@Client.on_callback_query(filters.regex("^withdraw$"))
async def withdraw_cb(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        user = await users_col.find_one({"_id": user_id})
        if not user or user.get("points", 0) < config.MIN_WITHDRAW:
            await callback_query.message.reply_text(
                f"Minimum {config.MIN_WITHDRAW} points required to withdraw.", quote=True
            )
            return await callback_query.answer()
        if user.get("pending_withdrawal"):
            await callback_query.message.reply_text("You already have a pending withdrawal request.", quote=True)
            return await callback_query.answer()
        await users_col.update_one({"_id": user_id}, {"$set": {"pending_withdrawal": user.get("points", 0)}})
        await callback_query.message.reply_text(
            "Withdrawal request submitted. Admin will review it soon.", quote=True
        )
        await callback_query.answer()
    except Exception as e:
        logger.exception("withdraw_cb failed: %s", e)


@Client.on_callback_query(filters.regex("^mypoints$"))
async def mypoints_cb(client, callback_query):
    try:
        data = await users_col.find_one({"_id": callback_query.from_user.id}) or {}
        points = data.get("points", 0)
        await callback_query.message.reply_text(
            f"You currently have <b>{points}</b> points.", quote=True
        )
        await callback_query.answer()
    except Exception as e:
        logger.exception("mypoints_cb failed: %s", e)


@Client.on_callback_query(filters.regex("^top$"))
async def top_cb(client, callback_query):
    try:
        top_users = users_col.find().sort("points", -1).limit(10)
        text = "<b>Top Users</b>\n"
        i = 1
        async for user in top_users:
            text += f"{i}. <code>{user['_id']}</code> - {user.get('points',0)} points\n"
            i += 1
        await callback_query.message.reply_text(text or "No data", quote=True)
        await callback_query.answer()
    except Exception as e:
        logger.exception("top_cb failed: %s", e)

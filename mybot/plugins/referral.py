from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from mybot.database.mongo import users_col
from mybot import config


# Callback: Show referral link and points
@Client.on_callback_query(filters.regex("^referral$"))
async def referral_cb(client, callback_query):
    user = callback_query.from_user
    bot = await client.get_me()

    link = f"https://t.me/{bot.username}?start={user.id}"
    data = await users_col.find_one({"_id": user.id}) or {}
    points = data.get("points", 0)

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
async def withdraw_cb(client, callback_query):
    user_id = callback_query.from_user.id
    user = await users_col.find_one({"_id": user_id})

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
    await users_col.update_one(
        {"_id": user_id},
        {"$set": {"pending_withdrawal": user.get("points", 0)}}
    )

    await callback_query.message.reply_text(
        "✅ Your withdrawal request has been submitted. An admin will review it soon.",
        quote=True
    )
    await callback_query.answer("Withdrawal request sent!")


# Callback: Show my points
@Client.on_callback_query(filters.regex("^mypoints$"))
async def mypoints_cb(client, callback_query):
    data = await users_col.find_one({"_id": callback_query.from_user.id}) or {}
    points = data.get("points", 0)

    await callback_query.message.reply_text(
        f"💎 You currently have <b>{points}</b> points.",
        parse_mode=ParseMode.HTML,
        quote=True
    )
    await callback_query.answer("Points displayed!")


# Callback: Show top 10 users by points
@Client.on_callback_query(filters.regex("^top$"))
async def top_cb(client, callback_query):
    top_users_cursor = users_col.find().sort("points", -1).limit(10)
    text = "🏆 <b>Top 10 Users</b>\n\n"
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

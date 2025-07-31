from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot.database.mongo import users_col
from mybot import config


@Client.on_callback_query(filters.regex("^admin$") & filters.user(config.OWNER_ID))
async def admin_panel(client, callback_query):
    await callback_query.message.reply_text(
        "Admin Commands:\n"
        "/points <user_id> - show user points\n"
        "/approve <user_id> - approve pending withdrawal\n"
        "/reject <user_id> - reject withdrawal",
        quote=True
    )
    await callback_query.answer()


@Client.on_message(filters.command("points") & filters.user(config.OWNER_ID))
async def points_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /points <user_id>")
    uid = int(message.command[1])
    user = await users_col.find_one({"_id": uid})
    if not user:
        await message.reply_text("User not found")
    else:
        await message.reply_text(f"User {uid} has {user.get('points',0)} points")


@Client.on_message(filters.command("approve") & filters.user(config.OWNER_ID))
async def approve_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /approve <user_id>")
    uid = int(message.command[1])
    user = await users_col.find_one({"_id": uid})
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text("No pending request for this user")
    amount = user.get("pending_withdrawal")
    if user.get("points", 0) < amount:
        return await message.reply_text("User has insufficient points")
    await users_col.update_one({"_id": uid}, {"$inc": {"points": -amount}, "$unset": {"pending_withdrawal": ""}})
    await message.reply_text(f"Withdrawal of {amount} points approved for {uid}")


@Client.on_message(filters.command("reject") & filters.user(config.OWNER_ID))
async def reject_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /reject <user_id>")
    uid = int(message.command[1])
    user = await users_col.find_one({"_id": uid})
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text("No pending request for this user")
    await users_col.update_one({"_id": uid}, {"$unset": {"pending_withdrawal": ""}})
    await message.reply_text(f"Withdrawal request from {uid} rejected")

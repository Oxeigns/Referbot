from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot.database.mongo import users_col, settings_col
from mybot import config
import logging

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^admin$") & filters.user(config.OWNER_ID))
async def admin_panel(client, callback_query):
    await callback_query.message.reply_text(
        "Admin Commands:\n"
        "/points <user_id> - show user points\n"
        "/approve <user_id> - approve pending withdrawal\n"
        "/reject <user_id> - reject withdrawal\n"
        "/setbutton <name> <value> - update button text/url\n"
        "/setchannels <ch1,ch2> - update required channels",
        quote=True
    )
    await callback_query.answer()


@Client.on_message(filters.command("points") & filters.user(config.OWNER_ID))
async def points_cmd(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("Usage: /points <user_id>")
        uid = int(message.command[1])
        user = await users_col.find_one({"_id": uid})
        if not user:
            await message.reply_text("User not found")
        else:
            await message.reply_text(f"User {uid} has {user.get('points',0)} points")
    except Exception as e:
        logger.exception("points_cmd failed: %s", e)


@Client.on_message(filters.command("setbutton") & filters.user(config.OWNER_ID))
async def setbutton_cmd(client, message):
    try:
        if len(message.command) < 3:
            return await message.reply_text("Usage: /setbutton <name> <value>")
        name = message.command[1]
        value = message.text.split(None, 2)[2]
        await settings_col.update_one({"_id": "buttons"}, {"$set": {name: value}}, upsert=True)
        await message.reply_text("Button updated")
    except Exception as e:
        logger.exception("setbutton failed: %s", e)


@Client.on_message(filters.command("setchannels") & filters.user(config.OWNER_ID))
async def setchannels_cmd(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("Usage: /setchannels <ch1,ch2>")
        channels = [ch.strip() for ch in message.text.split(None, 1)[1].split(',') if ch.strip()]
        await settings_col.update_one({"_id": "channels"}, {"$set": {"list": channels}}, upsert=True)
        await message.reply_text("Channels updated")
    except Exception as e:
        logger.exception("setchannels failed: %s", e)


@Client.on_message(filters.command("approve") & filters.user(config.OWNER_ID))
async def approve_cmd(client, message):
    try:
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
    except Exception as e:
        logger.exception("approve_cmd failed: %s", e)


@Client.on_message(filters.command("reject") & filters.user(config.OWNER_ID))
async def reject_cmd(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("Usage: /reject <user_id>")
        uid = int(message.command[1])
        user = await users_col.find_one({"_id": uid})
        if not user or not user.get("pending_withdrawal"):
            return await message.reply_text("No pending request for this user")
        await users_col.update_one({"_id": uid}, {"$unset": {"pending_withdrawal": ""}})
        await message.reply_text(f"Withdrawal request from {uid} rejected")
    except Exception as e:
        logger.exception("reject_cmd failed: %s", e)

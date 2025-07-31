from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot import config
from mybot.database.mongo import users_col, referrals_col, settings_col
import logging

logger = logging.getLogger(__name__)

BANNER_URL = config.BANNER_URL

WELCOME_TEXT = (
    "\ud83c\udfaf <b>Welcome to the Refer & Earn Bot</b>\n\n"
    "Invite friends and earn rewards!\n\n"
    "<b>1 Referral = 3 Points</b>\n"
    "<b>Minimum Withdrawal: 15 Points</b>"
)


async def get_start_keyboard(user_id: int):
    settings = await settings_col.find_one({"_id": "buttons"}) or {}
    help_text = settings.get("help_text", "\ud83d\udcdc Help")
    support_text = settings.get("support_text", "\ud83d\udcac Support")
    support_url = settings.get("support_url", "https://t.me/support")

    buttons = [
        [
            InlineKeyboardButton("\ud83d\udc8e Referral", callback_data="referral"),
            InlineKeyboardButton("\ud83d\udcb0 Withdraw", callback_data="withdraw"),
        ],
        [InlineKeyboardButton("\u2705 Verify Join", callback_data="verify")],
        [
            InlineKeyboardButton("\ud83d\udcca My Points", callback_data="mypoints"),
            InlineKeyboardButton("\ud83c\udfc6 Top Users", callback_data="top"),
        ],
        [
            InlineKeyboardButton(help_text, callback_data="help"),
            InlineKeyboardButton(support_text, url=support_url),
        ],
    ]
    if user_id == config.OWNER_ID:
        buttons.append([InlineKeyboardButton("\ud83d\udd27 Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(buttons)


@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    try:
        user_id = message.from_user.id
        args = message.command[1:]
        referrer = int(args[0]) if args and args[0].isdigit() else None

        user = await users_col.find_one({"_id": user_id})
        is_new = False
        if not user:
            is_new = True
            data = {"_id": user_id, "points": 0, "referred_by": referrer, "referrals": 0}
            await users_col.insert_one(data)
            if referrer and referrer != user_id:
                ref_user = await users_col.find_one({"_id": referrer})
                if ref_user:
                    await users_col.update_one({"_id": referrer}, {"$inc": {"points": 3, "referrals": 1}})
                    await referrals_col.insert_one({"referrer": referrer, "user": user_id})

        if is_new:
            try:
                text = (f"New user: {message.from_user.mention} (<code>{user_id}</code>)\n"
                        f"Referred by: <code>{referrer}</code>")
                await client.send_message(config.LOG_GROUP, text)
            except Exception as e:
                logger.error("Failed to log new user: %s", e)

        keyboard = await get_start_keyboard(user_id)
        await message.reply_photo(
            BANNER_URL,
            caption=WELCOME_TEXT,
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.exception("/start failed: %s", e)

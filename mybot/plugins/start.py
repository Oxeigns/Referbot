from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot import config
from mybot.database.mongo import users_col, referrals_col

BANNER_URL = "https://via.placeholder.com/600x300.png?text=Refer+%26+Earn"

WELCOME_TEXT = (
    "\ud83c\udfaf <b>Welcome to the Refer & Earn Bot</b>\n\n"
    "Invite friends and earn rewards!\n\n"
    "<b>1 Referral = 3 Points</b>\n"
    "<b>Minimum Withdrawal: 15 Points</b>"
)


def get_start_keyboard(user_id: int):
    buttons = [
        [InlineKeyboardButton("\ud83d\udc8e Referral", callback_data="referral"),
         InlineKeyboardButton("\ud83d\udcb0 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("\u2705 Verify Join", callback_data="verify")],
        [InlineKeyboardButton("\ud83d\udcca My Points", callback_data="mypoints"),
         InlineKeyboardButton("\ud83c\udfc6 Top Users", callback_data="top")],
        [InlineKeyboardButton("\ud83d\udcdc Help", callback_data="help"),
         InlineKeyboardButton("\ud83d\udcac Support", url="https://t.me/support")],
    ]
    if user_id == config.OWNER_ID:
        buttons.append([InlineKeyboardButton("\ud83d\udd27 Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(buttons)


@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    user_id = message.from_user.id
    args = message.command[1:]
    if args:
        referrer = int(args[0]) if args[0].isdigit() else None
    else:
        referrer = None

    user = await users_col.find_one({"_id": user_id})
    if not user:
        data = {"_id": user_id, "points": 0, "referred_by": referrer, "referrals": 0}
        await users_col.insert_one(data)
        if referrer and referrer != user_id:
            ref_user = await users_col.find_one({"_id": referrer})
            if ref_user:
                await users_col.update_one({"_id": referrer}, {"$inc": {"points": 3, "referrals": 1}})
                await referrals_col.insert_one({"referrer": referrer, "user": user_id})

    await message.reply_photo(
        BANNER_URL,
        caption=WELCOME_TEXT,
        reply_markup=get_start_keyboard(user_id),
    )

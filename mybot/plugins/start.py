from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot import config
from mybot.button import CHANNEL_LINKS, SUPPORT_URL
from mybot.database.mongo import users_col, referrals_col

# Banner image shown on /start
BANNER_URL = "https://via.placeholder.com/600x300.png?text=Refer+%26+Earn"

WELCOME_TEXT = (
    "🎯 <b>Welcome to the Refer & Earn Bot</b>\n\n"
    "Invite friends and earn rewards!\n\n"
    "<b>1 Referral = 3 Points</b>\n"
    "<b>Minimum Withdrawal: 15 Points</b>"
)


def get_start_keyboard(user_id: int) -> InlineKeyboardMarkup:
    join_buttons = [
        [InlineKeyboardButton(f"Join Channel {i + 1}", url=link)]
        for i, link in enumerate(CHANNEL_LINKS)
    ]

    buttons = list(join_buttons)
    buttons.append(
        [
            InlineKeyboardButton("💎 Referral", callback_data="referral"),
            InlineKeyboardButton("💰 Withdraw", callback_data="withdraw"),
        ]
    )

    if join_buttons:
        buttons.append([InlineKeyboardButton("✅ Verify Join", callback_data="verify")])

    buttons.append(
        [
            InlineKeyboardButton("📊 My Points", callback_data="mypoints"),
            InlineKeyboardButton("🏆 Top Users", callback_data="top"),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton("📜 Help", callback_data="help"),
            InlineKeyboardButton("💬 Support", url=SUPPORT_URL),
        ]
    )

    if user_id == config.OWNER_ID:
        buttons.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin")])

    return InlineKeyboardMarkup(buttons)


@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    referrer = None

    # Safely parse referral argument
    if len(parts) > 1:
        try:
            ref = int(parts[1])
            if ref != user_id:
                referrer = ref
        except ValueError:
            referrer = None

    try:
        # Ensure user exists
        user = await users_col.find_one({"_id": user_id})
        if not user:
            await users_col.insert_one(
                {"_id": user_id, "points": 0, "referred_by": referrer, "referrals": 0}
            )

            if referrer:
                ref_user = await users_col.find_one({"_id": referrer})
                if ref_user:
                    await users_col.update_one(
                        {"_id": referrer}, {"$inc": {"points": 3, "referrals": 1}}
                    )
                    await referrals_col.insert_one(
                        {"referrer": referrer, "user": user_id}
                    )

    except Exception as e:
        # Log database errors so they don't block responses
        print(f"DB error in /start: {e}")

    # Always respond even if DB fails
    await message.reply_photo(
        BANNER_URL,
        caption=WELCOME_TEXT,
        reply_markup=get_start_keyboard(user_id),
    )

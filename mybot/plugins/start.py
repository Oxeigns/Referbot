from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot import config
from mybot.database.mongo import users_col, referrals_col, settings_col

# Banner image shown on /start
BANNER_URL = "https://via.placeholder.com/600x300.png?text=Refer+%26+Earn"

WELCOME_TEXT = (
    "🎯 <b>Welcome to the Refer & Earn Bot</b>\n\n"
    "Invite friends and earn rewards!\n\n"
    "<b>1 Referral = 3 Points</b>\n"
    "<b>Minimum Withdrawal: 15 Points</b>"
)


def get_start_keyboard(user_id: int, join_buttons: list) -> InlineKeyboardMarkup:
    """Generate the main inline keyboard for the start panel."""
    buttons = join_buttons[:]

    buttons += [
        [
            InlineKeyboardButton("💎 Referral", callback_data="referral"),
            InlineKeyboardButton("💰 Withdraw", callback_data="withdraw")
        ],
    ]

    if join_buttons:
        buttons.append([InlineKeyboardButton("✅ Verify Join", callback_data="verify")])

    buttons += [
        [
            InlineKeyboardButton("📊 My Points", callback_data="mypoints"),
            InlineKeyboardButton("🏆 Top Users", callback_data="top")
        ],
        [
            InlineKeyboardButton("📜 Help", callback_data="help"),
            InlineKeyboardButton("💬 Support", url="https://t.me/support")
        ],
    ]

    # Show admin panel button only for OWNER
    if user_id == config.OWNER_ID:
        buttons.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin")])

    return InlineKeyboardMarkup(buttons)


@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    """
    /start command:
    - Handles referral links
    - Creates user in DB if new
    - Rewards referrer (3 points)
    - Shows stylish start panel
    """
    user_id = message.from_user.id
    args = message.command[1:]

    # Extract referrer ID from /start argument
    referrer = None
    if args and args[0].isdigit():
        referrer = int(args[0])

    # Check if user exists in DB
    user = await users_col.find_one({"_id": user_id})
    if not user:
        # Add new user
        await users_col.insert_one({
            "_id": user_id,
            "points": 0,
            "referred_by": referrer if (referrer and referrer != user_id) else None,
            "referrals": 0
        })

        # Reward referrer
        if referrer and referrer != user_id:
            ref_user = await users_col.find_one({"_id": referrer})
            if ref_user:
                await users_col.update_one(
                    {"_id": referrer},
                    {"$inc": {"points": 3, "referrals": 1}}
                )
                await referrals_col.insert_one({"referrer": referrer, "user": user_id})

    # Fetch channel buttons from DB
    doc = await settings_col.find_one({"_id": "channels"})
    join_buttons = []
    if doc:
        for num, link in sorted(doc.get("buttons", {}).items(), key=lambda x: int(x[0])):
            join_buttons.append([InlineKeyboardButton(f"Join Channel {num}", url=link)])

    # Send welcome banner and main menu
    await message.reply_photo(
        BANNER_URL,
        caption=WELCOME_TEXT,
        reply_markup=get_start_keyboard(user_id, join_buttons),
    )

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mybot.database.mongo import users_col, settings_col
from mybot import config


# Admin Panel callback button
@Client.on_callback_query(filters.regex("^admin$") & filters.user(config.OWNER_ID))
async def admin_panel(client, callback_query):
    text = (
        "🛠 <b>Admin Panel</b>\n\n"
        "Use the following commands:\n\n"
        "• <code>/points &lt;user_id&gt;</code> – Show user points\n"
        "• <code>/approve &lt;user_id&gt;</code> – Approve pending withdrawal\n"
        "• <code>/reject &lt;user_id&gt;</code> – Reject withdrawal request\n"
        "• <code>/add1 &lt;link&gt;</code> – Set channel button 1\n"
        "• <code>/add2 &lt;link&gt;</code> – Set channel button 2\n"
        "• <code>/add3 &lt;link&gt;</code> – Set channel button 3\n"
        "• <code>/remove1</code>, <code>/remove2</code>, <code>/remove3</code>\n"
        "• <code>/listchannels</code> – Show current channel buttons"
    )

    await callback_query.message.reply_text(
        text,
        quote=True,
        disable_web_page_preview=True
    )
    await callback_query.answer("Admin panel opened!")


# Show user points
@Client.on_message(filters.command("points") & filters.user(config.OWNER_ID))
async def points_cmd(_, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ <b>Usage:</b> <code>/points &lt;user_id&gt;</code>", parse_mode="html")

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID format.", parse_mode="html")

    user = await users_col.find_one({"_id": uid})
    if not user:
        return await message.reply_text(f"❌ No data found for user <code>{uid}</code>", parse_mode="html")

    points = user.get("points", 0)
    await message.reply_text(
        f"📊 <b>User:</b> <code>{uid}</code>\n"
        f"💎 <b>Points:</b> {points}",
        parse_mode="html"
    )


# Approve withdrawal
@Client.on_message(filters.command("approve") & filters.user(config.OWNER_ID))
async def approve_cmd(_, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ <b>Usage:</b> <code>/approve &lt;user_id&gt;</code>", parse_mode="html")

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID format.", parse_mode="html")

    user = await users_col.find_one({"_id": uid})
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text("❌ No pending withdrawal request for this user.", parse_mode="html")

    amount = user.get("pending_withdrawal")
    current_points = user.get("points", 0)

    if current_points < amount:
        return await message.reply_text("⚠️ Insufficient points in user's account.", parse_mode="html")

    await users_col.update_one(
        {"_id": uid},
        {"$inc": {"points": -amount}, "$unset": {"pending_withdrawal": ""}}
    )

    await message.reply_text(
        f"✅ Approved withdrawal of <b>{amount}</b> points for user <code>{uid}</code>",
        parse_mode="html"
    )


# Reject withdrawal
@Client.on_message(filters.command("reject") & filters.user(config.OWNER_ID))
async def reject_cmd(_, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ <b>Usage:</b> <code>/reject &lt;user_id&gt;</code>", parse_mode="html")

    try:
        uid = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID format.", parse_mode="html")

    user = await users_col.find_one({"_id": uid})
    if not user or not user.get("pending_withdrawal"):
        return await message.reply_text("❌ No pending withdrawal request for this user.", parse_mode="html")

    await users_col.update_one({"_id": uid}, {"$unset": {"pending_withdrawal": ""}})
    await message.reply_text(
        f"❌ Rejected withdrawal request from user <code>{uid}</code>",
        parse_mode="html"
    )


# -------------------------------------------------------------
# Channel management commands
# -------------------------------------------------------------

def _channel_doc():
    """Helper to get channel buttons document."""
    return settings_col.find_one({"_id": "channels"})


async def _update_button(num: str, link: str | None):
    if link:
        await settings_col.update_one(
            {"_id": "channels"},
            {"$set": {f"buttons.{num}": link}},
            upsert=True,
        )
    else:
        await settings_col.update_one(
            {"_id": "channels"},
            {"$unset": {f"buttons.{num}": ""}},
        )


async def _list_buttons() -> dict:
    doc = await _channel_doc()
    return doc.get("buttons", {}) if doc else {}


def owner_only(cmd: str):
    return Client.on_message(filters.command(cmd) & filters.user(config.OWNER_ID))


@owner_only("add1")
async def add1(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/add1 &lt;link&gt;</code>", parse_mode="html"
        )
    link = message.command[1]
    await _update_button("1", link)
    await message.reply_text(
        f"✅ Button 1 set to:\n<code>{link}</code>",
        parse_mode="html",
        disable_web_page_preview=True,
    )


@owner_only("add2")
async def add2(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/add2 &lt;link&gt;</code>", parse_mode="html"
        )
    link = message.command[1]
    await _update_button("2", link)
    await message.reply_text(
        f"✅ Button 2 set to:\n<code>{link}</code>",
        parse_mode="html",
        disable_web_page_preview=True,
    )


@owner_only("add3")
async def add3(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ <b>Usage:</b> <code>/add3 &lt;link&gt;</code>", parse_mode="html"
        )
    link = message.command[1]
    await _update_button("3", link)
    await message.reply_text(
        f"✅ Button 3 set to:\n<code>{link}</code>",
        parse_mode="html",
        disable_web_page_preview=True,
    )


@owner_only("remove1")
async def remove1(_, message):
    await _update_button("1", None)
    await message.reply_text("✅ Button 1 removed.", parse_mode="html")


@owner_only("remove2")
async def remove2(_, message):
    await _update_button("2", None)
    await message.reply_text("✅ Button 2 removed.", parse_mode="html")


@owner_only("remove3")
async def remove3(_, message):
    await _update_button("3", None)
    await message.reply_text("✅ Button 3 removed.", parse_mode="html")


@owner_only("listchannels")
async def list_channels(_, message):
    buttons = await _list_buttons()
    if not buttons:
        return await message.reply_text(
            "ℹ️ No channel buttons configured.", parse_mode="html"
        )

    text = "<b>Current Channel Buttons:</b>\n\n"
    for num, link in sorted(buttons.items(), key=lambda x: int(x[0])):
        text += f"{num}. <code>{link}</code>\n"
    await message.reply_text(
        text,
        parse_mode="html",
        disable_web_page_preview=True,
    )

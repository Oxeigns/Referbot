from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageNotModified
import logging

from mybot import config
from mybot.utils.decorators import log_errors

LOGGER = logging.getLogger(__name__)
LOGGER.info("Plugin loaded: %s", __name__)


def start_text() -> str:
    return (
        "🏆 <b>Welcome to Premium Bot</b>\n"
        "<i>Seamless referrals • Smart earnings • Zero hassle</i>"
    )


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎯 Referral Panel", callback_data="referral")],
            [InlineKeyboardButton("📚 Help & Commands", callback_data="help_menu")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about_menu")],
        ]
    )


def build_help_text(user_id: int) -> str:
    lines = [
        "╭─ 📚 <b>Command Panel</b> ─╮",
        "│ 🤖 <b>/start</b> – open dashboard",
        "│ 📡 <b>/ping</b> – check status",
        "│ 🧪 <b>/test</b> – run diagnostics",
    ]
    if user_id == config.OWNER_ID:
        lines.append("│ 📣 <b>/broadcast</b> – global announcement")
    lines.extend([
        "│ 🎯 Referral panel – use dashboard button",
        "╰───────────────────────╯",
    ])
    return "\n".join(lines)


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]
    )


async def safe_edit_text(message, text: str, **kwargs) -> None:
    """Edit message text if it actually changes.

    Telegram raises ``MessageNotModified`` when attempting to edit a message
    with identical content. Silently ignore this specific error to keep logs
    clean and avoid confusing users with unnecessary error messages.
    """
    try:
        await message.edit_text(text, **kwargs)
    except MessageNotModified:
        pass


@Client.on_message(filters.command(["start"]))
@log_errors
async def start_cmd(client: Client, message):
    LOGGER.info("/start from %s", message.from_user.id)
    await message.reply_text(
        start_text(),
        reply_markup=start_keyboard(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["help"]))
@log_errors
async def help_cmd(client: Client, message):
    LOGGER.info("/help from %s", message.from_user.id)
    help_message = build_help_text(message.from_user.id)
    await message.reply_text(
        help_message,
        reply_markup=back_keyboard(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["ping"]))
@log_errors
async def ping_cmd(client: Client, message):
    LOGGER.info("/ping from %s", message.from_user.id)
    await message.reply_text("Pong! ✅ Bot is online and running smoothly")


@Client.on_message(filters.command(["test"]))
@log_errors
async def test_cmd(client: Client, message):
    LOGGER.info("/test from %s", message.from_user.id)
    await message.reply_text("Test successful 🚀 Everything is working perfectly!")


@Client.on_callback_query(filters.regex("^(help_menu|about_menu|back_to_start)$"))
@log_errors
async def menu_callbacks(client: Client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    LOGGER.info("callback %s from %s", data, user_id)
    if data == "help_menu":
        await safe_edit_text(
            callback_query.message,
            build_help_text(user_id),
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        await callback_query.answer()
    elif data == "about_menu":
        about_text = (
            "🤖 <b>About This Bot</b>\n"
            "Version: 1.0\n"
            "Built with ❤️ using Pyrogram\n"
            "Developer: @oxeign"
        )
        await safe_edit_text(
            callback_query.message,
            about_text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        await callback_query.answer()
    elif data == "back_to_start":
        await safe_edit_text(
            callback_query.message,
            start_text(),
            reply_markup=start_keyboard(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        await callback_query.answer()

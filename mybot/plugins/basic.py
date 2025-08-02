from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import logging

from mybot import config
from mybot.utils.decorators import log_errors

LOGGER = logging.getLogger(__name__)


def start_text() -> str:
    return (
        "\uD83C\uDFC6 <b>Welcome to Premium Bot</b>\n"
        "<i>Seamless referrals • Smart earnings • Zero hassle</i>"
    )


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("\uD83C\uDFAF Referral Panel", callback_data="referral")],
            [InlineKeyboardButton("\uD83D\uDCD6 Help & Commands", callback_data="help_menu")],
            [InlineKeyboardButton("\u2139\uFE0F About", callback_data="about_menu")],
        ]
    )


def build_help_text(user_id: int) -> str:
    text = (
        "\uD83D\uDD0D *Modern Control Center*\n\n"
        "\uD83D\uDCCA *General Commands*\n"
        "• */start* – open dashboard\n"
        "• */ping* – check status\n"
        "• */test* – run diagnostics\n\n"
        "\uD83C\uDFAF *Referral System*\n"
        "Earn points by inviting friends\n"
    )
    if user_id == config.OWNER_ID:
        text += (
            "\n\uD83D\uDEE1 *Admin Commands*\n"
            "• */broadcast* – global announcement\n"
        )
    return text


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("\u2B05\uFE0F Back", callback_data="back_to_start")]]
    )


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
        parse_mode=ParseMode.MARKDOWN,
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
        await callback_query.message.edit_text(
            build_help_text(user_id),
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        await callback_query.answer()
    elif data == "about_menu":
        about_text = (
            "\uD83E\uDD16 <b>About This Bot</b>\n"
            "Version: 1.0\n"
            "Built with \u2764\uFE0F using Pyrogram\n"
            "Developer: @oxeign"
        )
        await callback_query.message.edit_text(
            about_text,
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        await callback_query.answer()
    elif data == "back_to_start":
        await callback_query.message.edit_text(
            start_text(),
            reply_markup=start_keyboard(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        await callback_query.answer()

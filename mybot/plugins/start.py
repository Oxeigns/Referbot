"""/start handler and home menu display."""

from __future__ import annotations

import logging

from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message

from ..ui import keyboards, messages
from ..utils import log_errors, notify_owner

LOGGER = logging.getLogger(__name__)


def _parse_referrer(argument: str | None) -> int | None:
    if not argument:
        return None
    argument = argument.strip()
    if argument.startswith("ref_"):
        argument = argument[4:]
    try:
        value = int(argument)
    except (ValueError, TypeError):
        return None
    return value if value > 0 else None


@Client.on_message(filters.private & filters.command("start"))
@log_errors
async def start_handler(client: Client, message: Message) -> None:
    user = message.from_user
    if not user:
        return
    context = client.app_context
    locale = user.language_code or context.config.locale
    referrer = None
    if message.command and len(message.command) > 1:
        referrer = _parse_referrer(message.command[1])
        if referrer == user.id:
            referrer = None
    profile = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "language_code": user.language_code,
    }
    user_doc = await client.user_service.ensure_user(
        user.id, referrer=referrer, profile=profile
    )
    created_at = user_doc.get("created_at")
    updated_at = user_doc.get("updated_at")
    is_new_user = bool(created_at and updated_at and created_at == updated_at)
    if referrer:
        existing = await client.referral_service.get(user.id)
        if not existing:
            referral_doc = await client.referral_service.create_pending(referrer, user.id)
            await notify_owner(
                client,
                (
                    "🤝 New referral pending\n"
                    f"Referrer: {referrer}\nUser: {user.id}\n"
                    f"Status: {referral_doc.get('status', 'pending')}"
                ),
            )
    home = messages.home_text(
        context.translator,
        locale=locale,
        user=user_doc,
        config=context.config,
        referral_link=context.referral_link(user.id),
    )
    keyboard = keyboards.home_keyboard(
        context.callback_signer,
        config=context.config,
        is_owner=user.id == context.config.owner_id,
    )
    photo_id: str | None = None
    try:
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos.total_count:
            photo_id = photos[0].file_id
    except RPCError as exc:  # pragma: no cover - network
        LOGGER.debug("Failed to fetch profile photo for %s: %s", user.id, exc)
    try:
        if photo_id:
            await message.reply_photo(
                photo_id,
                caption=home,
                reply_markup=keyboard,
                parse_mode="html",
            )
        else:
            await message.reply_photo(
                context.config.banner_url,
                caption=home,
                reply_markup=keyboard,
                parse_mode="html",
            )
    except RPCError:
        await message.reply_text(home, reply_markup=keyboard, disable_web_page_preview=True)

    await notify_owner(
        client,
        (
            "▶️ /start command\n"
            f"User: {user.id} ({user.first_name or ''})\n"
            f"Referrer: {referrer or '—'}"
        ),
    )
    if is_new_user:
        await notify_owner(
            client,
            (
                "🆕 New user joined\n"
                f"ID: {user.id}\nUsername: @{user.username if user.username else '—'}"
            ),
        )


@Client.on_message(filters.private & filters.command("help"))
@log_errors
async def help_handler(client: Client, message: Message) -> None:
    user = message.from_user
    if not user:
        return
    context = client.app_context
    locale = user.language_code or context.config.locale
    text = messages.help_text(context.translator, locale=locale, config=context.config)
    await message.reply_text(text, disable_web_page_preview=True, parse_mode="html")

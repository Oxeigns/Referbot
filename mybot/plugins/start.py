"""/start handler and home menu display."""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from ..ui import keyboards, messages
from ..utils import log_errors


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
    await client.user_service.ensure_user(user.id, referrer=referrer)
    if referrer:
        existing = await client.referral_service.get(user.id)
        if not existing:
            await client.referral_service.create_pending(referrer, user.id)
    home = messages.home_text(
        context.translator,
        locale=locale,
        user=await client.user_service.get(user.id),
        config=context.config,
    )
    keyboard = keyboards.home_keyboard(
        context.callback_signer,
        config=context.config,
        is_owner=user.id == context.config.owner_id,
    )
    await message.reply_text(home, reply_markup=keyboard, disable_web_page_preview=True)

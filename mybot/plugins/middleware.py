"""Common guards applied to all handlers."""

from __future__ import annotations

from pyrogram import Client, StopPropagation, filters
from pyrogram.types import CallbackQuery, Message

from ..ui import messages
from ..utils import log_errors


@Client.on_message(filters.private, group=-1)
@log_errors
async def guard_message(client: Client, message: Message) -> None:
    user = message.from_user
    if not user:
        raise StopPropagation
    context = client.app_context
    profile = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "language_code": user.language_code,
    }
    record = await client.user_service.ensure_user(user.id, profile=profile)
    locale = user.language_code or context.config.locale
    if record.get("banned"):
        await message.reply_text(messages.banned_text(context.translator, locale=locale))
        raise StopPropagation


@Client.on_callback_query(group=-1)
@log_errors
async def guard_callback(client: Client, callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        raise StopPropagation
    context = client.app_context
    record = await client.user_service.ensure_user(user.id)
    locale = user.language_code or context.config.locale
    if record.get("banned"):
        await callback.answer(messages.banned_text(context.translator, locale=locale), show_alert=True)
        raise StopPropagation

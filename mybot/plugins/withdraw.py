"""Withdrawal interaction handlers."""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from ..ui import messages
from ..utils import RateLimitExceeded, log_errors


@Client.on_message(filters.private & filters.text, group=1)
@log_errors
async def handle_withdraw_address(client: Client, message: Message) -> None:
    user = message.from_user
    if not user:
        return
    context = client.app_context
    pending = context.pending_withdrawals.get(user.id)
    if not pending or pending.get("stage") != "awaiting_address":
        return
    try:
        context.withdraw_rate_limiter.hit("withdraw", user.id)
    except RateLimitExceeded:
        await message.reply_text("Too many withdrawal attempts. Please wait before retrying.")
        return
    method = pending.get("method")
    if not method:
        await message.reply_text("Select a payout method first.")
        return
    address = message.text.strip()
    if len(address) < 3:
        await message.reply_text("Please provide a valid payout address.")
        return
    points = pending.get("points", 0)
    try:
        record = await client.withdrawal_service.request(
            user.id, points=points, method=method, address=address
        )
    except ValueError as exc:
        await message.reply_text(str(exc))
        context.pending_withdrawals.pop(user.id, None)
        return
    context.pending_withdrawals.pop(user.id, None)
    locale = user.language_code or context.config.locale
    text = messages.withdraw_confirmation_text(
        context.translator,
        locale=locale,
        points=record["points"],
        method=record["method"],
        address=record["address"],
    )
    await message.reply_text(text)
    owner_msg = (
        f"💸 Withdrawal request from {user.id}\n"
        f"Points: {record['points']}\nMethod: {record['method']}\nAddress: {record['address']}\n"
        f"Request ID: {record['_id']}"
    )
    await client.send_message(context.config.owner_id, owner_msg)

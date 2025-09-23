"""Utilities for sending out-of-band notifications."""

from __future__ import annotations

import logging

from pyrogram import Client
from pyrogram.errors import RPCError

LOGGER = logging.getLogger(__name__)


async def notify_owner(client: Client, text: str) -> None:
    """Send a direct message to the bot owner if logging is enabled."""

    if not text:
        return
    context = client.app_context
    if not context.config.owner_logs_enabled:
        return
    try:
        await client.send_message(context.config.owner_id, text)
    except RPCError as exc:  # pragma: no cover - network interaction
        LOGGER.warning("Failed to send owner notification: %s", exc)

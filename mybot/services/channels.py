"""Channel membership utilities."""

from __future__ import annotations

import asyncio
import logging
from typing import Sequence

from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError

from ..utils.retry import retry

LOGGER = logging.getLogger(__name__)


async def ensure_membership(client: Client, user_id: int, channels: Sequence[str]) -> bool:
    async def check(channel: str) -> bool:
        async def op():
            member = await client.get_chat_member(channel, user_id)
            status = getattr(member, "status", None)
            return status not in {"banned", "left", "kicked"}

        try:
            return await retry(lambda: op(), attempts=3, base_delay=1.0)
        except FloodWait as exc:  # pragma: no cover - network behavior
            await asyncio.sleep(exc.value)
            return await op()
        except RPCError as exc:  # pragma: no cover - network behavior
            LOGGER.warning("Failed to check membership for %s in %s: %s", user_id, channel, exc)
            return False

    results = await asyncio.gather(*(check(channel) for channel in channels))
    return all(results)

"""Channel membership utilities."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import MutableMapping, Sequence, Tuple

from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError

from ..utils.retry import retry

LOGGER = logging.getLogger(__name__)


async def ensure_membership(
    client: Client,
    user_id: int,
    channels: Sequence[str],
    *,
    cache: MutableMapping[Tuple[int, str], float],
    ttl: float = 300.0,
) -> tuple[bool, Sequence[str]]:
    """Check that a user has joined every required channel.

    Successful lookups are cached for a short period to avoid hitting rate
    limits repeatedly. Negative responses are never cached so that users can
    retry verification after fixing their membership status.
    """

    now = time.monotonic()
    missing: list[str] = []
    to_query = [channel for channel in channels if cache.get((user_id, channel), 0) <= now]

    async def check(channel: str) -> tuple[str, bool]:
        async def op() -> bool:
            member = await client.get_chat_member(channel, user_id)
            status = getattr(member, "status", None)
            return status not in {"banned", "left", "kicked"}

        try:
            result = await retry(op, attempts=3, base_delay=1.0)
        except ValueError as exc:
            LOGGER.warning(
                "Channel %s is not a joinable chat when checking user %s: %s",
                channel,
                user_id,
                exc,
            )
            result = False
        except FloodWait as exc:  # pragma: no cover - network behavior
            await asyncio.sleep(exc.value)
            result = await op()
        except RPCError as exc:  # pragma: no cover - network behavior
            LOGGER.warning(
                "Failed to check membership for user %s in %s: %s", user_id, channel, exc
            )
            result = False
        return channel, result

    if to_query:
        responses = await asyncio.gather(*(check(channel) for channel in to_query))
        for channel, ok in responses:
            key = (user_id, channel)
            if ok:
                cache[key] = now + ttl
            else:
                cache.pop(key, None)
                missing.append(channel)

    still_missing = [channel for channel in channels if (user_id, channel) not in cache and channel not in missing]
    missing.extend(still_missing)
    return len(missing) == 0, tuple(missing)


async def verify_bot_channel_access(client: Client, channels: Sequence[str]) -> Sequence[str]:
    """Return channels where the bot lacks access to view member lists."""

    if not channels:
        return tuple()

    bot = client.me
    if bot is None:
        bot = await client.get_me()

    async def check(channel: str) -> tuple[str, bool]:
        async def op() -> bool:
            member = await client.get_chat_member(channel, bot.id)
            status = getattr(member, "status", None)
            return status not in {"left", "kicked", "banned"}

        try:
            result = await retry(op, attempts=3, base_delay=1.0)
        except ValueError as exc:
            LOGGER.warning(
                "Channel %s is not a joinable chat when checking bot access: %s",
                channel,
                exc,
            )
            result = False
        except FloodWait as exc:  # pragma: no cover - network behavior
            await asyncio.sleep(exc.value)
            result = await op()
        except RPCError as exc:  # pragma: no cover - network behavior
            LOGGER.warning("Bot access check failed for %s: %s", channel, exc)
            result = False
        return channel, result

    responses = await asyncio.gather(*(check(channel) for channel in channels))
    failures = [channel for channel, ok in responses if not ok]
    return tuple(failures)

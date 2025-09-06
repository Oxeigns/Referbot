"""Application entry point for the Refer & Earn bot."""

from __future__ import annotations

import logging

from pyrogram import Client

from . import config

LOGGER = logging.getLogger(__name__)


def create_client() -> Client:
    """Construct the Pyrogram client with plugin loading enabled."""

    return Client(
        "referbot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        plugins=dict(root="mybot.plugins"),
    )


app = create_client()


def run() -> None:
    """Start the bot using long polling.

    The client automatically loads all handlers from the ``mybot.plugins``
    package so commands such as ``/start`` display the full start panel rather
    than a placeholder message.  Webhook execution is intentionally unsupported;
    when ``USE_WEBHOOK`` is set a warning is logged and the bot continues using
    long polling.
    """

    logging.basicConfig(level=getattr(logging, config.LOG_LEVEL, logging.INFO))
    if config.USE_WEBHOOK:
        LOGGER.warning(
            "Webhook mode requested but not supported; falling back to polling"
        )
    app.run()


if __name__ == "__main__":  # pragma: no cover - manual execution guard
    run()

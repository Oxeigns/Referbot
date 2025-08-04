"""Database utilities for the bot."""

import logging

from .mongo import db, mongo_client

LOGGER = logging.getLogger(__name__)


async def init_db() -> None:
    """Verify MongoDB connectivity."""
    try:
        await mongo_client.admin.command("ping")
    except Exception as exc:
        LOGGER.error("Failed to connect to MongoDB: %s", exc)
    else:
        LOGGER.info("MongoDB connection established")

"""Application entry point for the Refer & Earn bot."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from pyrogram import Client

from .config import CONFIG
from .context import AppContext
from .database.client import Database
from .services import AdminService, ReferralService, UserService, WithdrawalService
from .ui.i18n import Translator
from .utils.callbacks import CallbackSigner
from .utils.logging import setup_logging
from .utils.rate_limit import RateLimiter
from .webhooks.server import run_webhook

LOGGER = logging.getLogger(__name__)


class ReferBot(Client):
    def __init__(self, context: AppContext):
        super().__init__(
            "referbot",
            api_id=context.config.api_id,
            api_hash=context.config.api_hash,
            bot_token=context.config.bot_token,
            plugins={"root": "mybot.plugins"},
        )
        self.app_context = context
        self.user_service = UserService(context.database)
        self.referral_service = ReferralService(context.database)
        self.withdrawal_service = WithdrawalService(context.database)
        self.admin_service = AdminService(context)

    async def start(self):
        setup_logging(self.app_context.config.log_level)
        await self.app_context.database.connect()
        await super().start()
        self.app_context.bot_username = self.me.username
        LOGGER.info("Bot started as @%s", self.app_context.bot_username)

    async def stop(self, *args):  # type: ignore[override]
        await super().stop()
        await self.app_context.database.close()
        LOGGER.info("Bot stopped")


def build_context() -> AppContext:
    base_path = Path(__file__).resolve().parent
    translator = Translator.from_path(base_path / "ui" / "locales", default_locale=CONFIG.locale)
    database = Database(CONFIG.mongo_uri)
    signer = CallbackSigner(CONFIG.callback_secret)
    verify_limiter = RateLimiter(limit=1, window=30)
    withdraw_limiter = RateLimiter(limit=1, window=300)
    return AppContext(
        config=CONFIG,
        database=database,
        translator=translator,
        callback_signer=signer,
        verify_rate_limiter=verify_limiter,
        withdraw_rate_limiter=withdraw_limiter,
    )


def create_client() -> ReferBot:
    context = build_context()
    client = ReferBot(context)
    return client


def run() -> None:
    client = create_client()
    if CONFIG.use_webhook:
        asyncio.run(run_webhook(client))
    else:
        client.run()


if __name__ == "__main__":  # pragma: no cover
    run()

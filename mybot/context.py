"""Application context objects shared across handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .config import Config
from .database.client import Database
from .ui.i18n import Translator
from .utils.callbacks import CallbackSigner
from .utils.rate_limit import RateLimiter


@dataclass(slots=True)
class AdminState:
    """Tracks ongoing admin interactions awaiting additional input."""

    pending: Dict[int, dict] = field(default_factory=dict)

    def set(self, user_id: int, action: dict) -> None:
        self.pending[user_id] = action

    def get(self, user_id: int) -> dict | None:
        return self.pending.get(user_id)

    def pop(self, user_id: int) -> dict | None:
        return self.pending.pop(user_id, None)


@dataclass(slots=True)
class AppContext:
    config: Config
    database: Database
    translator: Translator
    callback_signer: CallbackSigner
    verify_rate_limiter: RateLimiter
    withdraw_rate_limiter: RateLimiter
    admin_state: AdminState = field(default_factory=AdminState)
    bot_username: str | None = None
    pending_withdrawals: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    channel_access_cache: Dict[Tuple[int, str], float] = field(default_factory=dict)

    def referral_link(self, user_id: int) -> str | None:
        if not self.bot_username:
            return None
        return f"https://t.me/{self.bot_username}?start=ref_{user_id}"

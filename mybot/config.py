"""Configuration management for the Refer & Earn bot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from dotenv import load_dotenv

__all__ = ["Config", "CONFIG", "ConfigError"]


class ConfigError(RuntimeError):
    """Raised when mandatory configuration values are missing or invalid."""


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"Invalid boolean value: {value!r}")


def _parse_int(name: str, value: str | None, *, minimum: int | None = None) -> int:
    if value is None:
        raise ConfigError(f"Environment variable {name} is required")
    try:
        integer = int(value)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ConfigError(f"Environment variable {name} must be an integer") from exc
    if minimum is not None and integer < minimum:
        raise ConfigError(f"Environment variable {name} must be >= {minimum}")
    return integer


def _parse_channels(value: str | None) -> List[str]:
    if not value:
        return []
    channels: list[str] = []
    for raw in value.split(","):
        chan = raw.strip()
        if not chan:
            continue
        if not chan.startswith("@") and not chan.startswith("https://t.me/"):
            raise ConfigError(
                "REQUIRED_CHANNELS entries must start with @username or https://t.me/"
            )
        channels.append(chan)
    return channels


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"Environment variable {name} is required")
    return value


@dataclass(slots=True)
class Config:
    api_id: int
    api_hash: str
    bot_token: str
    owner_id: int
    mongo_uri: str
    callback_secret: str
    use_webhook: bool
    webhook_url: str | None
    port: int
    ref_points_per_ref: int
    min_withdraw_points: int
    required_channels: List[str]
    support_url: str | None
    log_level: str
    locale: str

    def channels_display(self) -> Sequence[str]:
        return tuple(self.required_channels)


def load_config() -> Config:
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:  # pragma: no cover - .env absence is acceptable
        load_dotenv()

    api_id = _parse_int("API_ID", os.getenv("API_ID"), minimum=1)
    api_hash = _require("API_HASH")
    bot_token = _require("BOT_TOKEN")
    owner_id = _parse_int("OWNER_ID", os.getenv("OWNER_ID"), minimum=1)
    mongo_uri = _require("MONGO_URI")
    callback_secret = _require("CALLBACK_SECRET")
    if len(callback_secret) < 16:
        raise ConfigError("CALLBACK_SECRET must be at least 16 characters long")

    use_webhook = _parse_bool(os.getenv("USE_WEBHOOK"), default=False)
    webhook_url = os.getenv("WEBHOOK_URL")
    if use_webhook and not webhook_url:
        raise ConfigError("WEBHOOK_URL must be set when USE_WEBHOOK is enabled")

    port = _parse_int("PORT", os.getenv("PORT", "8080"), minimum=1)

    ref_points = _parse_int(
        "REF_POINTS_PER_REF", os.getenv("REF_POINTS_PER_REF", "1"), minimum=1
    )
    min_withdraw = _parse_int(
        "MIN_WITHDRAW_POINTS",
        os.getenv("MIN_WITHDRAW_POINTS", "1"),
        minimum=1,
    )
    required_channels = _parse_channels(os.getenv("REQUIRED_CHANNELS"))
    support_url = os.getenv("SUPPORT_URL")
    log_level = (os.getenv("LOG_LEVEL") or "INFO").upper()
    locale = os.getenv("LOCALE", "en")

    return Config(
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        owner_id=owner_id,
        mongo_uri=mongo_uri,
        callback_secret=callback_secret,
        use_webhook=use_webhook,
        webhook_url=webhook_url,
        port=port,
        ref_points_per_ref=ref_points,
        min_withdraw_points=min_withdraw,
        required_channels=required_channels,
        support_url=support_url,
        log_level=log_level,
        locale=locale,
    )


CONFIG = load_config()

"""Pure functions returning user facing messages."""

from __future__ import annotations

from typing import Any, Dict, Sequence

from ..config import Config
from .i18n import Translator


def home_text(
    translator: Translator,
    *,
    locale: str,
    user: Dict[str, Any],
    config: Config,
    referral_link: str | None,
) -> str:
    return translator.t(
        "home.intro",
        locale=locale,
        first_name=user.get("profile", {}).get("first_name", "Friend"),
        points=user.get("points", 0),
        min_withdraw=config.min_withdraw_points,
        ref_points=config.ref_points_per_ref,
        referral_link=referral_link or "N/A",
    )


def referral_link_text(translator: Translator, *, locale: str, link: str) -> str:
    return translator.t("referral.link", locale=locale, link=link)


def points_text(translator: Translator, *, locale: str, points: int, stats: Dict[str, int]) -> str:
    return translator.t(
        "points.summary",
        locale=locale,
        points=points,
        pending=stats.get("pending", 0),
        qualified=stats.get("qualified", 0),
        rejected=stats.get("rejected", 0),
    )


def verify_success_text(translator: Translator, *, locale: str, ref_points: int) -> str:
    return translator.t("verify.success", locale=locale, points=ref_points)


def verify_failure_text(
    translator: Translator,
    *,
    locale: str,
    channels: Sequence[str],
    missing: Sequence[str],
) -> str:
    required = "\n".join(f"• {channel}" for channel in channels)
    missing_list = "\n".join(f"• {channel}" for channel in missing) or "• —"
    return translator.t(
        "verify.failure",
        locale=locale,
        channels=required,
        missing=missing_list,
    )


def withdraw_prompt_text(translator: Translator, *, locale: str, minimum: int) -> str:
    return translator.t("withdraw.prompt", locale=locale, minimum=minimum)


def withdraw_confirmation_text(
    translator: Translator,
    *,
    locale: str,
    points: int,
    method: str,
    address: str,
) -> str:
    return translator.t(
        "withdraw.confirmation",
        locale=locale,
        points=points,
        method=method,
        address=address,
    )


def leaderboard_text(translator: Translator, *, locale: str, entries: Sequence[Dict[str, Any]]) -> str:
    if not entries:
        return translator.t("leaderboard.empty", locale=locale)
    lines = [translator.t("leaderboard.header", locale=locale)]
    for index, doc in enumerate(entries, start=1):
        name = doc.get("profile", {}).get("first_name") or str(doc.get("_id"))
        points = doc.get("points", 0)
        lines.append(f"{index}. {name} — {points}")
    return "\n".join(lines)


def banned_text(translator: Translator, *, locale: str) -> str:
    return translator.t("user.banned", locale=locale)


def admin_panel_text(translator: Translator, *, locale: str) -> str:
    return translator.t("admin.intro", locale=locale)


def settings_updated_text(translator: Translator, *, locale: str) -> str:
    return translator.t("admin.settings_updated", locale=locale)


def broadcast_report_text(translator: Translator, *, locale: str, delivered: int) -> str:
    return translator.t("admin.broadcast_complete", locale=locale, delivered=delivered)


def channels_overview_text(
    translator: Translator, *, locale: str, channels: Sequence[str]
) -> str:
    listing = "\n".join(f"• {channel}" for channel in channels) or "• —"
    return translator.t("channels.list", locale=locale, channels=listing)


def help_text(translator: Translator, *, locale: str, config: Config) -> str:
    return translator.t(
        "help.text",
        locale=locale,
        support_url=config.support_url or "https://t.me/oxeign",
        min_withdraw=config.min_withdraw_points,
        ref_points=config.ref_points_per_ref,
    )

"""View builders returning text and keyboard."""
from __future__ import annotations

from typing import List, Tuple

from .formatting import html_escape, username_short, points_fmt
from .keyboards import (
    home as kb_home,
    verify as kb_verify,
    referral as kb_referral,
    leaderboard as kb_leaderboard,
    withdrawals_list as kb_withdrawals,
    confirm_withdraw as kb_confirm_withdraw,
)
from .strings import t
from .style import EMOJIS, SYMBOLS


def home_view(user: dict) -> Tuple[str, 'InlineKeyboardMarkup']:
    """Render home view for user."""
    from pyrogram.types import InlineKeyboardMarkup

    locale = user.get("locale", "en")
    name = username_short(html_escape(user.get("name", "User")))
    points = points_fmt(user.get("points", 0))
    refs = points_fmt(user.get("refs", 0))
    today = points_fmt(user.get("today", 0))
    text = (
        f"<b>{t('home.title', locale)}</b>\n"
        f"{t('home.subtitle', locale, name=name)}\n"
        f"• Points: <b>{points}</b>\n"
        f"• Referrals: <b>{refs}</b>\n"
        f"• Today: <b>{today}</b>"
    )
    if not user.get("verified", True):
        text += f"\n\n{t('home.tip', locale)}"
    keyboard = kb_home(locale, user.get("is_owner", False))
    return text, keyboard


def verify_view(channels_status: List[dict], locale: str) -> Tuple[str, 'InlineKeyboardMarkup']:
    """Render verification status view."""
    from pyrogram.types import InlineKeyboardMarkup

    lines = [f"<b>{t('verify.title', locale)}</b>"]
    all_joined = True
    for ch in channels_status:
        handle = ch.get("handle")
        title = ch.get("title", "")
        name = f"@{handle}" if handle else title
        joined = ch.get("joined")
        mark = SYMBOLS['check'] if joined else SYMBOLS['cross']
        if not joined:
            all_joined = False
        lines.append(f"{html_escape(name)}  {mark}")
    lines.append(
        t("verify.all_set", locale) if all_joined else t("verify.join_then_recheck", locale)
    )
    text = "\n".join(lines)
    keyboard = kb_verify(channels_status, locale)
    return text, keyboard


def referral_view(user: dict, link: str) -> Tuple[str, 'InlineKeyboardMarkup']:
    """Render referral info view."""
    from pyrogram.types import InlineKeyboardMarkup

    locale = user.get("locale", "en")
    points = points_fmt(user.get("points", 0))
    refs = points_fmt(user.get("refs", 0))
    today = points_fmt(user.get("today", 0))
    lines = [
        f"<b>{t('referral.title', locale)}</b>",
        t('referral.share', locale),
        f"<code>{html_escape(link)}</code>",
        t("referral.stats", locale, points=points, refs=refs, today=today),
    ]
    text = "\n".join(lines)
    keyboard = kb_referral(locale, link, user.get("eligible_withdraw", False))
    return text, keyboard


def leaderboard_view(items: List[dict], your_rank: dict, page: int, total_pages: int, locale: str) -> Tuple[str, 'InlineKeyboardMarkup']:
    """Render leaderboard view."""
    from pyrogram.types import InlineKeyboardMarkup

    lines = [f"<b>{t('leaderboard.title', locale)}</b>"]
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for item in items:
        name = html_escape(username_short(item.get("name", "User")))
        rank = item.get("rank")
        medal = medals.get(rank)
        pts = points_fmt(item.get("points", 0))
        if medal:
            lines.append(f"{medal} {name} ({pts} pts)")
        else:
            lines.append(f"#{rank} — {name} ({pts} pts)")
    lines.append(
        t(
            "leaderboard.your_rank",
            locale,
            rank=your_rank.get("rank", 0),
            points=points_fmt(your_rank.get("points", 0)),
        )
    )
    text = "\n".join(lines)
    keyboard = kb_leaderboard(locale, page, total_pages)
    return text, keyboard


def withdrawals_view(items: List[dict], balance: int, min_withdraw: int, page: int, total_pages: int, locale: str) -> Tuple[str, 'InlineKeyboardMarkup']:
    """Render withdrawals list view."""
    from pyrogram.types import InlineKeyboardMarkup

    status_map = {
        "pending": EMOJIS["pending"],
        "approved": EMOJIS["approved"],
        "rejected": EMOJIS["rejected"],
    }
    lines = [
        f"<b>{t('withdraw.title', locale)}</b>",
        t("withdraw.balance", locale, balance=balance, min=min_withdraw),
    ]
    for w in items:
        lines.append(
            t(
                "withdraw.item",
                locale,
                id=w.get("id"),
                amount=w.get("amount"),
                status=status_map.get(w.get("status"), ""),
            )
        )
    text = "\n".join(lines)
    keyboard = kb_withdrawals(locale, page, total_pages)
    return text, keyboard


def confirm_withdraw_view(amount: int, balance_after: int, locale: str) -> Tuple[str, 'InlineKeyboardMarkup']:
    """Render withdrawal confirmation view."""
    from pyrogram.types import InlineKeyboardMarkup

    lines = [
        f"<b>{t('confirm.title', locale)}</b>",
        t("confirm.amount", locale, amount=amount),
        t("confirm.balance_after", locale, balance_after=balance_after),
    ]
    text = "\n".join(lines)
    keyboard = kb_confirm_withdraw(locale, amount)
    return text, keyboard

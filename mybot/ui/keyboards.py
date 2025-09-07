"""Inline keyboard builders."""
from __future__ import annotations

import os
from typing import List

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .callbacks import build
from .strings import t
from .style import EMOJIS

SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/support")


def nav_back_home(locale: str, back_to: str = "home:open") -> List[List[InlineKeyboardButton]]:
    """Return navigation footer with back and home buttons."""
    return [[
        InlineKeyboardButton(t("nav.back", locale), callback_data=build({"route": back_to})),
        InlineKeyboardButton(t("nav.home", locale), callback_data=build({"route": "home:open"})),
    ]]


def page_controls(locale: str, page: int, total_pages: int, prefix: str) -> List[List[InlineKeyboardButton]]:
    """Pagination control row."""
    if total_pages <= 1:
        return []
    prev_route = f"{prefix}:page:{page - 1}" if page > 1 else "noop"
    next_route = f"{prefix}:page:{page + 1}" if page < total_pages else "noop"
    row = [
        InlineKeyboardButton(EMOJIS["prev"], callback_data=build({"route": prev_route})),
        InlineKeyboardButton(f"Page {page}/{total_pages}", callback_data=build({"route": "noop"})),
        InlineKeyboardButton(EMOJIS["next"], callback_data=build({"route": next_route})),
    ]
    return [row]


def home(locale: str, is_owner: bool) -> InlineKeyboardMarkup:
    """Home panel keyboard."""
    rows: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(f"{EMOJIS['verify']} Verify", callback_data=build({"route": "verify:open"})),
            InlineKeyboardButton(f"{EMOJIS['referral']} Referral", callback_data=build({"route": "ref:open"})),
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['top']} Top", callback_data=build({"route": "top:open:1"})),
            InlineKeyboardButton(f"{EMOJIS['withdraw']} Withdraw", callback_data=build({"route": "wd:list:1"})),
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['help']} Help", callback_data=build({"route": "help:open"})),
            InlineKeyboardButton(f"{EMOJIS['support']} Support", url=SUPPORT_URL),
        ],
    ]
    if is_owner:
        rows.append([
            InlineKeyboardButton(f"{EMOJIS['admin']} Admin", callback_data=build({"route": "admin:open:broadcast"})),
        ])
    return InlineKeyboardMarkup(rows)


def verify(channels_status: List[dict], locale: str) -> InlineKeyboardMarkup:
    """Verify screen keyboard."""
    rows: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton("🔁 Re-check", callback_data=build({"route": "verify:recheck"}))]
    ]
    rows += nav_back_home(locale)
    return InlineKeyboardMarkup(rows)


def referral(locale: str, link: str, can_withdraw: bool) -> InlineKeyboardMarkup:
    """Referral panel keyboard."""
    rows: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(f"{EMOJIS['share']} Share", callback_data=build({"route": "ref:share"})),
            InlineKeyboardButton(f"{EMOJIS['how']} How", callback_data=build({"route": "ref:how"})),
        ]
    ]
    row2 = [InlineKeyboardButton(f"{EMOJIS['stats']} Stats", callback_data=build({"route": "ref:stats"}))]
    if can_withdraw:
        row2.append(InlineKeyboardButton(f"{EMOJIS['withdraw']} Withdraw", callback_data=build({"route": "wd:list:1"})))
    rows.append(row2)
    rows += nav_back_home(locale)
    return InlineKeyboardMarkup(rows)


def leaderboard(locale: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = []
    rows += page_controls(locale, page, total_pages, "top")
    rows += nav_back_home(locale)
    return InlineKeyboardMarkup(rows)


def withdrawals_list(locale: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(t("withdraw.request", locale), callback_data=build({"route": "wd:req"}))]
    ]
    rows += page_controls(locale, page, total_pages, "wd:list")
    rows += nav_back_home(locale)
    return InlineKeyboardMarkup(rows)


def confirm_withdraw(locale: str, amount: int) -> InlineKeyboardMarkup:
    rows: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton("Confirm", callback_data=build({"route": f"wd:confirm:{amount}"}))]
    ]
    rows += nav_back_home(locale, back_to="wd:list:1")
    return InlineKeyboardMarkup(rows)


def admin_tabs(active: str, locale: str) -> InlineKeyboardMarkup:
    tabs = ["broadcast", "users", "withdrawals", "settings"]
    buttons: List[InlineKeyboardButton] = []
    for tab in tabs:
        text = t(f"admin.tabs.{tab}", locale)
        if tab == active:
            buttons.append(InlineKeyboardButton(f"• {text}", callback_data=build({"route": "noop"})))
        else:
            buttons.append(InlineKeyboardButton(text, callback_data=build({"route": f"admin:open:{tab}"})))
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows += nav_back_home(locale, back_to="home:open")
    return InlineKeyboardMarkup(rows)

"""Inline keyboard builders."""

from __future__ import annotations

from typing import Sequence

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..config import Config
from ..utils.callbacks import CallbackSigner


def home_keyboard(
    signer: CallbackSigner,
    *,
    config: Config,
    is_owner: bool,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    rows.append(
        [InlineKeyboardButton("📣 Join Channels", callback_data=signer.pack("channels"))]
    )
    rows.append(
        [InlineKeyboardButton("✅ Verify", callback_data=signer.pack("verify"))]
    )
    rows.append(
        [
            InlineKeyboardButton("🎁 My Link", callback_data=signer.pack("link")),
            InlineKeyboardButton("📊 My Points", callback_data=signer.pack("points")),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton("🏆 Top Users", callback_data=signer.pack("leaderboard")),
            InlineKeyboardButton("🧾 Withdraw", callback_data=signer.pack("withdraw")),
        ]
    )
    support_button = (
        InlineKeyboardButton("💬 Support", url=config.support_url)
        if config.support_url
        else InlineKeyboardButton("💬 Support", callback_data=signer.pack("support"))
    )
    rows.append(
        [
            support_button,
            InlineKeyboardButton("ℹ️ Help / Commands", callback_data=signer.pack("help")),
        ]
    )
    if is_owner:
        rows.append(
            [InlineKeyboardButton("🛠 Admin Panel", callback_data=signer.pack("admin"))]
        )
    return InlineKeyboardMarkup(rows)


def channels_keyboard(signer: CallbackSigner, channels: Sequence[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for channel in channels:
        rows.append([InlineKeyboardButton(channel, url=_normalise_channel(channel))])
    if not rows:
        rows.append([InlineKeyboardButton("No channels configured", callback_data=signer.pack("noop"))])
    return InlineKeyboardMarkup(rows)


def withdraw_method_keyboard(signer: CallbackSigner) -> InlineKeyboardMarkup:
    methods = ["UPI", "Paytm", "USDT"]
    rows = [[InlineKeyboardButton(method, callback_data=signer.pack("withdraw_method", {"method": method}))] for method in methods]
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data=signer.pack("home"))])
    return InlineKeyboardMarkup(rows)


def admin_panel_keyboard(signer: CallbackSigner) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("📢 Broadcast", callback_data=signer.pack("admin:broadcast")),
            InlineKeyboardButton("👥 Users", callback_data=signer.pack("admin:users")),
        ],
        [
            InlineKeyboardButton("🤝 Referrals", callback_data=signer.pack("admin:referrals")),
            InlineKeyboardButton("💸 Payouts", callback_data=signer.pack("admin:payouts")),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data=signer.pack("admin:settings")),
            InlineKeyboardButton("🏠 Home", callback_data=signer.pack("home")),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def admin_broadcast_keyboard(signer: CallbackSigner) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("All Users", callback_data=signer.pack("admin:broadcast_all"))],
        [InlineKeyboardButton("Active Users", callback_data=signer.pack("admin:broadcast_active"))],
        [InlineKeyboardButton("Points ≥ threshold", callback_data=signer.pack("admin:broadcast_filtered"))],
        [InlineKeyboardButton("⬅️ Back", callback_data=signer.pack("admin"))],
    ]
    return InlineKeyboardMarkup(rows)


def admin_users_keyboard(signer: CallbackSigner) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🔍 Search", callback_data=signer.pack("admin:users_search"))],
        [InlineKeyboardButton("🚫 Ban", callback_data=signer.pack("admin:users_ban"))],
        [InlineKeyboardButton("✅ Unban", callback_data=signer.pack("admin:users_unban"))],
        [InlineKeyboardButton("➕/➖ Points", callback_data=signer.pack("admin:users_points"))],
        [InlineKeyboardButton("📄 Export CSV", callback_data=signer.pack("admin:users_export"))],
        [InlineKeyboardButton("⬅️ Back", callback_data=signer.pack("admin"))],
    ]
    return InlineKeyboardMarkup(rows)


def admin_referrals_keyboard(signer: CallbackSigner) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Pending", callback_data=signer.pack("admin:referrals_pending"))],
        [InlineKeyboardButton("Qualified", callback_data=signer.pack("admin:referrals_qualified"))],
        [InlineKeyboardButton("⬅️ Back", callback_data=signer.pack("admin"))],
    ]
    return InlineKeyboardMarkup(rows)


def admin_payouts_keyboard(signer: CallbackSigner) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Pending", callback_data=signer.pack("admin:payouts_pending"))],
        [InlineKeyboardButton("Mark Approved", callback_data=signer.pack("admin:payouts_approve"))],
        [InlineKeyboardButton("Reject", callback_data=signer.pack("admin:payouts_reject"))],
        [InlineKeyboardButton("Mark Paid", callback_data=signer.pack("admin:payouts_paid"))],
        [InlineKeyboardButton("⬅️ Back", callback_data=signer.pack("admin"))],
    ]
    return InlineKeyboardMarkup(rows)


def admin_settings_keyboard(signer: CallbackSigner) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Points per referral", callback_data=signer.pack("admin:settings_ref_points"))],
        [InlineKeyboardButton("Minimum withdrawal", callback_data=signer.pack("admin:settings_min_withdraw"))],
        [
            InlineKeyboardButton("Manage channels", callback_data=signer.pack("admin:settings_channels")),
            InlineKeyboardButton("Support URL", callback_data=signer.pack("admin:settings_support")),
        ],
        [
            InlineKeyboardButton("Banner URL", callback_data=signer.pack("admin:settings_banner")),
            InlineKeyboardButton("Toggle owner logs", callback_data=signer.pack("admin:settings_owner_logs")),
        ],
        [InlineKeyboardButton("Test channels access", callback_data=signer.pack("admin:settings_test_channels"))],
        [InlineKeyboardButton("⬅️ Back", callback_data=signer.pack("admin"))],
    ]
    return InlineKeyboardMarkup(rows)


def _normalise_channel(channel: str) -> str:
    return channel if channel.startswith("http") else f"https://t.me/{channel.lstrip('@')}"

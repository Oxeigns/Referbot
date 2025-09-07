"""Referral UI plugin skeleton."""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from ..services import Services
from ..ui import views, callbacks


def register(app: Client, services: Services) -> None:
    @app.on_callback_query(filters.create(lambda _, __, q: callbacks.parse(q.data).get("route") == "ref:open"))
    async def _open(client: Client, query: CallbackQuery):
        profile = services.get_profile(query.from_user.id)
        link = services.resolve_share_link(query.from_user.id)
        text, kb = views.referral_view(profile, link)
        await query.message.edit_text(text, reply_markup=kb, parse_mode="html")
        await query.answer()

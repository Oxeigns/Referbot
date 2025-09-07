"""Leaderboard UI plugin skeleton."""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from ..services import Services
from ..ui import views, callbacks
from ..ui.style import LAYOUT


def register(app: Client, services: Services) -> None:
    @app.on_callback_query(filters.create(lambda _, __, q: callbacks.parse(q.data).get("route", "").startswith("top:open")))
    async def _open(client: Client, query: CallbackQuery):
        data = callbacks.parse(query.data)
        page = int(data.get("route", "top:open:1").split(":")[-1])
        lb = services.get_leaderboard(page, LAYOUT["page_size"])
        rank = services.get_user_rank(query.from_user.id)
        text, kb = views.leaderboard_view(lb["items"], rank, page, lb.get("total", 0), services.get_profile(query.from_user.id).get("locale", "en"))
        await query.message.edit_text(text, reply_markup=kb, parse_mode="html")
        await query.answer()

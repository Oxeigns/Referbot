"""Withdrawals UI plugin skeleton."""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from ..services import Services
from ..ui import views, callbacks
from ..ui.style import LAYOUT


def register(app: Client, services: Services) -> None:
    @app.on_callback_query(filters.create(lambda _, __, q: callbacks.parse(q.data).get("route", "").startswith("wd:list")))
    async def _list(client: Client, query: CallbackQuery):
        data = callbacks.parse(query.data)
        page = int(data.get("route", "wd:list:1").split(":")[-1])
        profile = services.get_profile(query.from_user.id)
        withdrawals = services.list_withdrawals(query.from_user.id, page, LAYOUT["page_size"])
        text, kb = views.withdrawals_view(withdrawals["items"], profile.get("points", 0), 0, page, withdrawals.get("total", 0), profile.get("locale", "en"))
        await query.message.edit_text(text, reply_markup=kb, parse_mode="html")
        await query.answer()

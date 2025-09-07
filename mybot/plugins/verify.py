"""Verification UI plugin skeleton."""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from ..services import Services
from ..ui import views, keyboards, callbacks


def register(app: Client, services: Services) -> None:
    @app.on_callback_query(filters.create(lambda _, __, q: callbacks.parse(q.data).get("route") == "verify:open"))
    async def _open(client: Client, query: CallbackQuery):
        channels = services.get_verification_status(query.from_user.id)
        text, kb = views.verify_view(channels, services.get_profile(query.from_user.id).get("locale", "en"))
        await query.message.edit_text(text, reply_markup=kb, parse_mode="html")
        await query.answer()

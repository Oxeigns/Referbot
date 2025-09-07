"""Help UI plugin skeleton."""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from ..services import Services
from ..ui import callbacks


def register(app: Client, services: Services) -> None:
    @app.on_callback_query(filters.create(lambda _, __, q: callbacks.parse(q.data).get("route") == "help:open"))
    async def _open(client: Client, query: CallbackQuery):
        await query.answer("Coming soon", show_alert=True)

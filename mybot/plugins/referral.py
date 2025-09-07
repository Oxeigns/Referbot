"""Referral UI plugin skeleton."""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from ..services import Services, MemoryServices
from ..ui import views, callbacks
from ..main import app


def register(app: Client, services: Services) -> None:
    """Register callback handler for the referral panel.

    The original implementation exposed a ``register`` function but never
    invoked it, meaning the ``ref:open`` callback went unhandled and the
    Referral Panel button appeared non-functional.  We keep the function for
    extensibility but also call it automatically with a lightweight in-memory
    service implementation so the button works out of the box.
    """

    @app.on_callback_query(
        filters.create(lambda _, __, q: callbacks.parse(q.data).get("route") == "ref:open")
    )
    async def _open(client: Client, query: CallbackQuery):
        profile = services.get_profile(query.from_user.id)
        link = services.resolve_share_link(query.from_user.id)
        text, kb = views.referral_view(profile, link)
        await query.message.edit_text(text, reply_markup=kb, parse_mode="html")
        await query.answer()


# Automatically register using an in-memory service so the referral panel works
# during tests and basic usage.
register(app, MemoryServices())

"""Home plugin using UI views."""
from __future__ import annotations

from pyrogram import Client, filters

from ..services import Services
from ..ui import views


async def start_handler(client: Client, message, services: Services):
    user = services.get_profile(message.from_user.id)
    user["name"] = message.from_user.first_name or "User"
    text, keyboard = views.home_view(user)
    await message.reply_text(text, reply_markup=keyboard, parse_mode="html")


def register(app: Client, services: Services) -> None:
    @app.on_message(filters.command("start"))
    async def _start(client, message):
        await start_handler(client, message, services)

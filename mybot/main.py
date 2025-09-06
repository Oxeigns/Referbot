import os
from pyrogram import Client, filters

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

PORT = int(os.environ.get("PORT", "8080"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Client("escrow-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply_text("Webhook mode ✅")


def run() -> None:
    """Start the bot using long polling.

    Pyrogram's :meth:`Client.run` in version 2 does not accept webhook
    parameters like ``port`` or ``webhook``. Passing them results in a
    ``TypeError``.  This helper keeps the bot operational by starting it in
    polling mode. Hosting platforms that require a webhook should configure the
    web server separately and forward updates to the bot.
    """

    app.run()


if __name__ == "__main__":  # pragma: no cover - manual execution guard
    run()

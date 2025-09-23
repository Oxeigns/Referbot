"""FastAPI server used in webhook deployments."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
import uvicorn

from ..utils.logging import setup_logging

LOGGER = logging.getLogger(__name__)


def create_app(client) -> FastAPI:
    app = FastAPI()

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/telegram")
    async def telegram(request: Request) -> dict[str, Any]:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != client.app_context.config.callback_secret:
            raise HTTPException(status_code=401, detail="invalid secret token")
        payload = await request.json()
        LOGGER.debug("Webhook payload received: %s", payload)
        # Updates continue to be processed via the MTProto connection managed by Pyrogram.
        return {"ok": True}

    return app


async def configure_webhook(client) -> None:
    config = client.app_context.config
    if not config.webhook_url:
        LOGGER.warning("WEBHOOK_URL is not configured; running webhook server without Telegram callback")
        return
    payload = {
        "url": config.webhook_url,
        "secret_token": config.callback_secret,
        "drop_pending_updates": True,
    }
    api_url = f"https://api.telegram.org/bot{config.bot_token}/setWebhook"
    async with httpx.AsyncClient(timeout=10.0) as session:
        response = await session.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Failed to set webhook: {data}")
    LOGGER.info("Webhook configured at %s", config.webhook_url)


async def delete_webhook(client) -> None:
    config = client.app_context.config
    api_url = f"https://api.telegram.org/bot{config.bot_token}/deleteWebhook"
    async with httpx.AsyncClient(timeout=10.0) as session:
        try:
            response = await session.post(api_url, json={"drop_pending_updates": False})
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network interaction
            LOGGER.warning("Failed to delete webhook: %s", exc)


async def run_webhook(client) -> None:
    await client.start()
    setup_logging(client.app_context.config.log_level)
    app = create_app(client)
    try:
        await configure_webhook(client)
    except Exception as exc:
        LOGGER.error("Webhook configuration failed: %s", exc)
    config = uvicorn.Config(app, host="0.0.0.0", port=client.app_context.config.port, log_level="info")
    server = uvicorn.Server(config)
    LOGGER.info("Webhook server listening on port %s", client.app_context.config.port)
    try:
        await server.serve()
    finally:
        await delete_webhook(client)
        await client.stop()

"""FastAPI server used in webhook deployments."""

from __future__ import annotations

import logging
from typing import Any

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


async def run_webhook(client) -> None:
    await client.start()
    setup_logging(client.app_context.config.log_level)
    app = create_app(client)
    config = uvicorn.Config(app, host="0.0.0.0", port=client.app_context.config.port, log_level="info")
    server = uvicorn.Server(config)
    LOGGER.info("Webhook server listening on port %s", client.app_context.config.port)
    try:
        await server.serve()
    finally:
        await client.stop()

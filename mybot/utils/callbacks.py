"""HMAC based callback signing utilities."""

from __future__ import annotations

import base64
import hashlib
import hmac
import urllib.parse
from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True)
class CallbackPayload:
    action: str
    data: Dict[str, str]


class CallbackSigner:
    def __init__(self, secret: str):
        self._secret = secret.encode("utf-8")

    def _signature(self, payload: str) -> str:
        digest = hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest[:8]).decode("utf-8").rstrip("=")

    def pack(self, action: str, data: Dict[str, str] | None = None) -> str:
        data = data or {}
        query = "&".join(
            f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in sorted(data.items())
        )
        payload = f"{action}:{query}" if query else action
        token = f"{payload}|{self._signature(payload)}"
        if len(token.encode("utf-8")) > 64:
            raise ValueError("Callback payload exceeds 64 bytes")
        return token

    def unpack(self, token: str) -> CallbackPayload:
        try:
            payload, signature = token.rsplit("|", 1)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError("Malformed callback payload") from exc
        expected = self._signature(payload)
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid callback signature")
        if ":" in payload:
            action, query = payload.split(":", 1)
            data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
        else:
            action, data = payload, {}
        return CallbackPayload(action=action, data=data)

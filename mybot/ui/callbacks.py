"""HMAC-signed callback data utilities."""
from __future__ import annotations

import base64
import json
import os
import hmac
import hashlib
from typing import Any, Dict

SECRET = os.getenv("CALLBACK_SECRET", "test_secret").encode()


def _sign(data: bytes) -> str:
    return hmac.new(SECRET, data, hashlib.sha256).hexdigest()


def build(data: Dict[str, Any]) -> str:
    """Serialize and sign data for callback_data."""
    raw = json.dumps(data, separators=(",", ":")).encode()
    sig = _sign(raw)
    payload = base64.urlsafe_b64encode(raw).decode()
    return f"{payload}:{sig}"


def parse(payload: str) -> Dict[str, Any]:
    """Validate signature and return data."""
    try:
        data_b64, sig = payload.split(":", 1)
        raw = base64.urlsafe_b64decode(data_b64.encode())
    except Exception as e:  # pragma: no cover - invalid encoding
        raise ValueError("Invalid payload") from e
    if _sign(raw) != sig:
        raise ValueError("Bad signature")
    return json.loads(raw.decode())

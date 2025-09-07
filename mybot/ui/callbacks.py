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

    # ``callback_data`` has a hard limit of 64 bytes.  The original
    # implementation stored the full 64 character HMAC digest which pushed the
    # payload well over Telegram's limit and resulted in ``BUTTON_DATA_INVALID``
    # errors when sending the ``/start`` keyboards.  We trim the digest and
    # strip Base64 padding to keep the encoded data compact while still
    # providing a lightweight integrity check.
    sig = _sign(raw)[:8]  # first 4 bytes of the hex digest
    payload = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    return f"{payload}:{sig}"


def parse(payload: str) -> Dict[str, Any]:
    """Validate signature and return data."""
    try:
        data_b64, sig = payload.split(":", 1)

        # Add missing Base64 padding before decoding
        padding = "=" * (-len(data_b64) % 4)
        raw = base64.urlsafe_b64decode((data_b64 + padding).encode())
    except Exception as e:  # pragma: no cover - invalid encoding
        raise ValueError("Invalid payload") from e
    if _sign(raw)[:8] != sig:
        raise ValueError("Bad signature")
    return json.loads(raw.decode())

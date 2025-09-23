import os
import sys
from pathlib import Path

os.environ.setdefault("API_ID", "1")
os.environ.setdefault("API_HASH", "hash")
os.environ.setdefault("BOT_TOKEN", "token")
os.environ.setdefault("OWNER_ID", "1")
os.environ.setdefault("MONGO_URI", "mongodb://localhost/test")
os.environ.setdefault("CALLBACK_SECRET", "supersecretkeythatislongenough")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mybot.utils.callbacks import CallbackSigner


def test_callback_signer_roundtrip():
    signer = CallbackSigner("supersecretkeythatislongenough")
    token = signer.pack("action", {"foo": "bar", "id": "42"})
    payload = signer.unpack(token)
    assert payload.action == "action"
    assert payload.data["foo"] == "bar"
    assert payload.data["id"] == "42"
    assert len(token.encode("utf-8")) <= 64

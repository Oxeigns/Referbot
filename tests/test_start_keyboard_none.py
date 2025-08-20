import importlib
import sys
from pathlib import Path

# Ensure project root on path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import mybot.button as button
import mybot.plugins.start as start


def test_start_keyboard_handles_none(monkeypatch):
    # simulate misconfiguration where CHANNEL_LINKS is None
    monkeypatch.setattr(button, "CHANNEL_LINKS", None)
    importlib.reload(start)

    kb = start.get_start_keyboard(42)

    # ensure there are no join or verify buttons
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert all(not text.startswith("Join Channel") for text in texts)
    assert not any("Verify" in text for text in texts)

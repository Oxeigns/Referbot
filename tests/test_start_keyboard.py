import importlib
import sys
from pathlib import Path

# Ensure the project root is on the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import mybot.button as button
import mybot.config as config
import mybot.plugins.start as start


def test_start_keyboard(monkeypatch):
    test_channels = [
        "https://t.me/channel1",
        "https://t.me/channel2",
        "https://t.me/channel3",
    ]
    owner_id = 12345
    non_owner_id = 54321

    # Patch configuration values
    monkeypatch.setattr(button, "CHANNEL_LINKS", test_channels)
    monkeypatch.setattr(config, "OWNER_ID", owner_id)

    # Reload start module to apply patched channel links
    importlib.reload(start)

    # Generate keyboards for owner and non-owner
    owner_keyboard = start.get_start_keyboard(owner_id)
    user_keyboard = start.get_start_keyboard(non_owner_id)

    # Count join buttons
    def count_join_buttons(keyboard):
        return sum(
            1
            for row in keyboard.inline_keyboard
            for btn in row
            if btn.text.startswith("Join Channel")
        )

    assert count_join_buttons(owner_keyboard) == len(test_channels)

    # Admin Panel should be present for owner
    owner_texts = [btn.text for row in owner_keyboard.inline_keyboard for btn in row]
    user_texts = [btn.text for row in user_keyboard.inline_keyboard for btn in row]

    assert any("Admin Panel" in text for text in owner_texts)
    assert all("Admin Panel" not in text for text in user_texts)

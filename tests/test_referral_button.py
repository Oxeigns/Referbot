import importlib
import sys
from pathlib import Path

# Ensure project root on path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from mybot.ui import callbacks
import mybot.plugins.start as start
import mybot.plugins.basic as basic


def _find_button(kb, text):
    for row in kb.inline_keyboard:
        for btn in row:
            if btn.text == text:
                return btn
    raise AssertionError(f"Button with text {text} not found")


def test_start_referral_button_callback():
    kb = start.get_start_keyboard(123)
    btn = _find_button(kb, "💎 Referral")
    data = callbacks.parse(btn.callback_data)
    assert data["route"] == "ref:open"


def test_basic_referral_button_callback():
    kb = basic.start_keyboard()
    btn = _find_button(kb, "🎯 Referral Panel")
    data = callbacks.parse(btn.callback_data)
    assert data["route"] == "ref:open"

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

from mybot.config import Config
from mybot.ui.keyboards import home_keyboard
from mybot.utils.callbacks import CallbackSigner


def make_config(**overrides):
    base = dict(
        api_id=1,
        api_hash="hash",
        bot_token="token",
        owner_id=10,
        mongo_uri="mongodb://localhost/test",
        mongo_db="test",
        callback_secret="supersecretkeythatislongenough",
        use_webhook=False,
        webhook_url=None,
        port=8080,
        ref_points_per_ref=5,
        min_withdraw_points=20,
        required_channels=["@channel1", "@channel2"],
        support_url="https://t.me/support",
        banner_url="https://example.com/banner.jpg",
        log_level="INFO",
        locale="en",
        owner_logs_enabled=True,
    )
    base.update(overrides)
    return Config(**base)


def test_home_keyboard_contains_admin_button_for_owner():
    config = make_config()
    signer = CallbackSigner(config.callback_secret)
    keyboard = home_keyboard(signer, config=config, is_owner=True)
    assert any("Admin" in button.text for row in keyboard.inline_keyboard for button in row)


def test_home_keyboard_hides_admin_for_regular_user():
    config = make_config()
    signer = CallbackSigner(config.callback_secret)
    keyboard = home_keyboard(signer, config=config, is_owner=False)
    assert all("Admin" not in button.text for row in keyboard.inline_keyboard for button in row)


def test_home_keyboard_includes_help_button():
    config = make_config()
    signer = CallbackSigner(config.callback_secret)
    keyboard = home_keyboard(signer, config=config, is_owner=False)
    assert any(
        "Help" in button.text for row in keyboard.inline_keyboard for button in row
    )

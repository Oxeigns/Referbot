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
from mybot.ui import messages, i18n


def make_config(**overrides):
    base = dict(
        api_id=1,
        api_hash="hash",
        bot_token="token",
        owner_id=10,
        mongo_uri="mongodb://localhost/test",
        callback_secret="supersecretkeythatislongenough",
        use_webhook=False,
        webhook_url=None,
        port=8080,
        ref_points_per_ref=5,
        min_withdraw_points=20,
        required_channels=["@channel1"],
        support_url=None,
        log_level="INFO",
        locale="en",
    )
    base.update(overrides)
    return Config(**base)


def test_home_text_contains_dynamic_values():
    config = make_config()
    translator = i18n.Translator.from_path(Path("mybot/ui/locales"))
    user = {"profile": {"first_name": "Alice"}, "points": 10}
    text = messages.home_text(translator, locale="en", user=user, config=config)
    assert "Alice" in text
    assert str(config.min_withdraw_points) in text
    assert str(config.ref_points_per_ref) in text

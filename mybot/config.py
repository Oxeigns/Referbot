import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file into environment variables
load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Owner (admin) Telegram user ID
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")

# Optional log group ID (for new user logs)
LOG_GROUP = os.getenv("LOG_GROUP")  # e.g., -1001234567890

# Logging level. Defaults to INFO if not set.
# Example values: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Referral/withdrawal settings
MIN_WITHDRAW = 15

# Optional banner shown in the bot and webhook toggle.
BANNER_URL = os.getenv("BANNER_URL")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() in {"1", "true", "yes"}


@dataclass
class Config:
    """Runtime configuration container."""

    BOT_TOKEN: str
    BANNER_URL: str | None
    USE_WEBHOOK: bool


def load_config() -> Config:
    """Load configuration values into a dataclass.

    The module level constants remain for backwards compatibility with
    existing code (and tests), while this helper offers a convenient structured
    way for new code to access configuration.
    """

    return Config(BOT_TOKEN=BOT_TOKEN, BANNER_URL=BANNER_URL, USE_WEBHOOK=USE_WEBHOOK)

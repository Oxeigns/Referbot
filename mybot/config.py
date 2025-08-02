import os
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

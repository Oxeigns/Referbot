import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MONGO_URI = os.getenv("MONGO_URI")
CHANNELS = [ch.strip() for ch in os.getenv("CHANNELS", "").split(',') if ch.strip()]

MIN_WITHDRAW = 15

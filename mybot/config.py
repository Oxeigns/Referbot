import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_GROUP = int(os.getenv("LOG_GROUP"))
MONGO_URI = os.getenv("MONGO_URI")
CHANNELS = [ch.strip() for ch in os.getenv("CHANNELS", "").split(',') if ch.strip()]

MIN_WITHDRAW = 15
BANNER_URL="https://via.placeholder.com/600x300.png?text=Refer+%26+Earn"

from motor.motor_asyncio import AsyncIOMotorClient
from mybot import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client.get_default_database()

users_col = db["users"]
referrals_col = db["referrals"]

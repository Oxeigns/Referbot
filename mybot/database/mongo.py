from motor.motor_asyncio import AsyncIOMotorClient
from mybot import config

mongo_client = AsyncIOMotorClient(config.MONGO_URI)
db = mongo_client["refer_bot"]

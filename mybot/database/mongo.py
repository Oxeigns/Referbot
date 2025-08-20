from motor.motor_asyncio import AsyncIOMotorClient
from mybot import config

mongo_client = AsyncIOMotorClient(config.MONGO_URI)
db = mongo_client["refer_bot"]

# Collections used across the bot
users_col = db["users"]
referrals_col = db["referrals"]


async def init_indexes() -> None:
    """Ensure required MongoDB indexes exist."""

    try:
        await users_col.create_index("referrer")
        await referrals_col.create_index([("referrer", 1), ("user", 1)], unique=True)
    except Exception:
        # Index creation failures shouldn't crash the bot at startup.
        pass

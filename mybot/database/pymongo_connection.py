import logging
import time
from pymongo import MongoClient

# A placeholder MongoDB URI. Replace with your actual connection string.
MONGO_URI = "your-mongodb-uri"


def connect_to_mongo():
    """Establish a resilient connection to MongoDB.

    Logs connection attempts and retries up to three times with exponential
    backoff before giving up. Longer timeouts are used to better handle slow
    network conditions or cold starts often experienced on cloud platforms like
    Render.
    """
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    # Suppressing DEBUG heartbeat messages keeps production logs concise and
    # avoids revealing internal driver details.

    for attempt in range(3):
        logging.info("Connecting to MongoDB...")
        try:
            client = MongoClient(
                MONGO_URI,
                # 30s timeouts accommodate slow connections or cold starts
                # that are common when deploying on platforms like Render.
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
            )
            client.admin.command("ping")
        except Exception as exc:
            if attempt == 2:
                raise Exception("Failed to connect to MongoDB after 3 attempts") from exc
            wait = 2 ** (attempt + 1)
            logging.warning(
                "Connection failed. Retrying in %s seconds...", wait
            )
            time.sleep(wait)
        else:
            logging.info("MongoDB connection established")
            return client


def main():
    connect_to_mongo()
    print("Connected!")


if __name__ == "__main__":
    main()

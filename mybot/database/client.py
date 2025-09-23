"""MongoDB client helpers and index creation utilities."""

from __future__ import annotations

import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import ASCENDING, IndexModel
from pymongo.errors import ConfigurationError

LOGGER = logging.getLogger(__name__)


class Database:
    """Thin wrapper around :class:`AsyncIOMotorClient` with index helpers."""

    def __init__(self, uri: str, *, db_name: str | None = None):
        self._uri = uri
        self._db_name = db_name
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    @property
    def client(self) -> AsyncIOMotorClient:
        if self._client is None:
            raise RuntimeError("Database client is not connected")
        return self._client

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("Database is not initialized")
        return self._db

    @property
    def users(self) -> AsyncIOMotorCollection:
        return self.db["users"]

    @property
    def referrals(self) -> AsyncIOMotorCollection:
        return self.db["referrals"]

    @property
    def withdrawals(self) -> AsyncIOMotorCollection:
        return self.db["withdrawals"]

    async def connect(self) -> None:
        if self._client is not None:
            return
        self._client = AsyncIOMotorClient(self._uri, uuidRepresentation="standard")
        database = None
        if self._db_name:
            database = self._client[self._db_name]
        else:
            try:
                database = self._client.get_default_database()
            except ConfigurationError:
                LOGGER.warning(
                    "MONGO_URI does not define a default database; falling back to 'referbot'."
                )
        if database is None:
            fallback = self._db_name or "referbot"
            database = self._client[fallback]
        self._db = database
        await self.ensure_indexes()

    async def ensure_indexes(self) -> None:
        """Ensure indexes for all collections (idempotent)."""

        if self._db is None:
            raise RuntimeError("Database must be connected before creating indexes")

        await self.users.create_indexes(
            [
                IndexModel([("referrer", ASCENDING)]),
                IndexModel([("banned", ASCENDING)]),
                IndexModel([("created_at", ASCENDING)]),
            ]
        )
        await self.referrals.create_indexes(
            [
                IndexModel([("referrer", ASCENDING), ("user", ASCENDING)], unique=True),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", ASCENDING)]),
            ]
        )
        await self.withdrawals.create_indexes(
            [
                IndexModel([("user", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", ASCENDING)]),
            ]
        )
        LOGGER.info("Database indexes ensured")

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None

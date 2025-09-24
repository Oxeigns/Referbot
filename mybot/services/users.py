"""User management service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
from pymongo import ReturnDocument

from ..database.client import Database


@dataclass(slots=True)
class UserRecord:
    _id: int
    points: int
    referrer: int | None
    banned: bool
    created_at: datetime
    updated_at: datetime


class UserService:
    def __init__(self, database: Database):
        self.db = database

    async def get(self, user_id: int) -> Dict[str, Any] | None:
        return await self.db.users.find_one({"_id": user_id})

    async def ensure_user(self, user_id: int, *, referrer: int | None = None, profile: Dict[str, Any] | None = None) -> Dict[str, Any]:
        now = datetime.utcnow()
        profile = profile or {}
        update = {
            "$setOnInsert": {
                "_id": user_id,
                "points": 0,
                "referrer": referrer,
                "banned": False,
                "created_at": now,
            },
            "$set": {
                "updated_at": now,
                **{f"profile.{key}": value for key, value in profile.items()},
            },
        }
        if referrer is not None:
            update["$setOnInsert"].setdefault("referrer", referrer)
        document = await self.db.users.find_one_and_update(
            {"_id": user_id},
            update,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        assert document is not None  # pragma: no cover - guaranteed by upsert
        return document

    async def assign_referrer(self, user_id: int, referrer: int) -> Dict[str, Any] | None:
        """Assign a referrer to a user if none has been recorded yet."""

        if referrer == user_id:
            return None
        now = datetime.utcnow()
        return await self.db.users.find_one_and_update(
            {
                "_id": user_id,
                "$or": [
                    {"referrer": None},
                    {"referrer": {"$exists": False}},
                ],
            },
            {"$set": {"referrer": referrer, "updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )

    async def add_points(self, user_id: int, points: int) -> Dict[str, Any] | None:
        now = datetime.utcnow()
        return await self.db.users.find_one_and_update(
            {"_id": user_id},
            {"$inc": {"points": points}, "$set": {"updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )

    async def set_banned(self, user_id: int, banned: bool) -> Dict[str, Any] | None:
        now = datetime.utcnow()
        return await self.db.users.find_one_and_update(
            {"_id": user_id},
            {"$set": {"banned": banned, "updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )

    async def top_users(self, *, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.db.users.find({"banned": False}).sort("points", -1).limit(limit)
        return [doc async for doc in cursor]

    async def search(self, query: str, *, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            numeric_id = int(query)
        except ValueError:
            numeric_id = None
        filters: list[dict[str, Any]] = []
        if numeric_id is not None:
            filters.append({"_id": numeric_id})
        filters.append({"profile.username": {"$regex": query, "$options": "i"}})
        filters.append({"profile.first_name": {"$regex": query, "$options": "i"}})
        if not filters:
            return []
        cursor = self.db.users.find({"$or": filters}).limit(limit)
        return [doc async for doc in cursor]

    async def export_csv_rows(self) -> List[List[str]]:
        header = ["user_id", "points", "referrer", "banned", "created_at", "updated_at"]
        rows = [header]
        async for doc in self.db.users.find({}, projection={"profile": 0}):
            rows.append(
                [
                    str(doc.get("_id")),
                    str(doc.get("points", 0)),
                    str(doc.get("referrer", "")),
                    str(doc.get("banned", False)),
                    doc.get("created_at").isoformat() if doc.get("created_at") else "",
                    doc.get("updated_at").isoformat() if doc.get("updated_at") else "",
                ]
            )
        return rows

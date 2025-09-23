"""Referral domain logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pymongo import ReturnDocument
from ..database.client import Database


class ReferralService:
    def __init__(self, database: Database):
        self.db = database

    async def create_pending(self, referrer: int, user: int) -> Dict[str, Any]:
        now = datetime.utcnow()
        referral = await self.db.referrals.find_one_and_update(
            {"user": user},
            {
                "$setOnInsert": {
                    "referrer": referrer,
                    "user": user,
                    "status": "pending",
                    "created_at": now,
                },
                "$set": {"updated_at": now},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        assert referral is not None
        return referral

    async def get(self, user: int) -> Dict[str, Any] | None:
        return await self.db.referrals.find_one({"user": user})

    async def qualify(self, user: int) -> Dict[str, Any] | None:
        now = datetime.utcnow()
        referral = await self.db.referrals.find_one_and_update(
            {"user": user, "status": "pending"},
            {
                "$set": {
                    "status": "qualified",
                    "qualified_at": now,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return referral

    async def reject(self, user: int, reason: str | None = None) -> Dict[str, Any] | None:
        now = datetime.utcnow()
        update = {"$set": {"status": "rejected", "updated_at": now}}
        if reason:
            update["$set"]["reason"] = reason
        return await self.db.referrals.find_one_and_update(
            {"user": user},
            update,
            return_document=ReturnDocument.AFTER,
        )

    async def list_by_status(self, status: str, *, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.db.referrals.find({"status": status}).sort("created_at", -1).limit(limit)
        return [doc async for doc in cursor]

    async def stats(self, referrer: int) -> Dict[str, int]:
        pipeline = [
            {"$match": {"referrer": referrer}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        counts: Dict[str, int] = {"pending": 0, "qualified": 0, "rejected": 0}
        async for doc in self.db.referrals.aggregate(pipeline):
            counts[doc["_id"]] = doc["count"]
        return counts

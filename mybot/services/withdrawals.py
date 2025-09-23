"""Withdrawal management service layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId
from pymongo import ReturnDocument

from ..database.client import Database


class WithdrawalService:
    def __init__(self, database: Database):
        self.db = database

    async def request(
        self,
        user_id: int,
        *,
        points: int,
        method: str,
        address: str,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        user = await self.db.users.find_one_and_update(
            {"_id": user_id, "points": {"$gte": points}},
            {"$inc": {"points": -points}, "$set": {"updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        if not user:
            raise ValueError("Insufficient balance")
        document = {
            "user": user_id,
            "points": points,
            "method": method,
            "address": address,
            "status": "requested",
            "created_at": now,
        }
        result = await self.db.withdrawals.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def set_status(
        self,
        withdrawal_id: ObjectId,
        *,
        status: str,
        acted_by: int,
    ) -> Dict[str, Any] | None:
        now = datetime.utcnow()
        update = {"$set": {"status": status, "acted_at": now, "acted_by": acted_by}}
        return await self.db.withdrawals.find_one_and_update(
            {"_id": withdrawal_id},
            update,
            return_document=ReturnDocument.AFTER,
        )

    async def list_by_status(self, status: str, *, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = (
            self.db.withdrawals.find({"status": status}).sort("created_at", -1).limit(limit)
        )
        return [doc async for doc in cursor]

    async def history(self, user_id: int, *, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = (
            self.db.withdrawals.find({"user": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [doc async for doc in cursor]

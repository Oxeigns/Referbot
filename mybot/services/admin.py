"""Administrative utility functions supporting the owner control panel."""

from __future__ import annotations

import csv
import io
import logging
from typing import Any, AsyncIterator, Dict, List

from pyrogram import Client
from pyrogram.errors import RPCError

from ..context import AppContext
from pymongo import ReturnDocument

LOGGER = logging.getLogger(__name__)


class AdminService:
    def __init__(self, context: AppContext):
        self.context = context

    async def iter_user_ids(self, *, active_only: bool = False) -> AsyncIterator[int]:
        query: dict[str, Any] = {}
        if active_only:
            query["banned"] = False
        cursor = self.context.database.users.find(query, projection={"_id": 1})
        async for doc in cursor:
            yield doc["_id"]

    async def broadcast(
        self,
        client: Client,
        message: str,
        *,
        scope: str = "all",
        min_points: int = 0,
    ) -> int:
        delivered = 0
        async for user_id in self.iter_user_ids(active_only=(scope != "all")):
            if scope == "filtered":
                user = await self.context.database.users.find_one({"_id": user_id})
                if not user or user.get("points", 0) < min_points:
                    continue
            try:
                await client.send_message(user_id, message)
                delivered += 1
            except RPCError as exc:  # pragma: no cover - network issues
                LOGGER.warning("Broadcast to %s failed: %s", user_id, exc)
        return delivered

    async def export_users_csv(self) -> io.BytesIO:
        cursor = self.context.database.users.find({}, projection={"profile": 0})
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["user_id", "points", "referrer", "banned", "created_at", "updated_at"])
        async for doc in cursor:
            writer.writerow(
                [
                    doc.get("_id"),
                    doc.get("points", 0),
                    doc.get("referrer"),
                    doc.get("banned", False),
                    doc.get("created_at"),
                    doc.get("updated_at"),
                ]
            )
        buffer = io.BytesIO(output.getvalue().encode("utf-8"))
        buffer.seek(0)
        return buffer

    async def set_ban(self, user_id: int, banned: bool) -> Dict[str, Any] | None:
        return await self.context.database.users.find_one_and_update(
            {"_id": user_id},
            {"$set": {"banned": banned}},
            return_document=ReturnDocument.AFTER,
        )

    async def adjust_points(self, user_id: int, *, delta: int) -> Dict[str, Any] | None:
        return await self.context.database.users.find_one_and_update(
            {"_id": user_id},
            {"$inc": {"points": delta}},
            return_document=ReturnDocument.AFTER,
        )

    async def list_referrals(self, status: str, *, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = self.context.database.referrals.find({"status": status}).sort("created_at", -1).limit(limit)
        return [doc async for doc in cursor]

    async def list_withdrawals(self, status: str, *, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = (
            self.context.database.withdrawals.find({"status": status})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [doc async for doc in cursor]

    async def update_setting(self, key: str, value: Any) -> None:
        settings_collection = self.context.database.db["settings"]
        await settings_collection.update_one(
            {"_id": "runtime"},
            {"$set": {key: value}},
            upsert=True,
        )

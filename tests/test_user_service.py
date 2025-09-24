import asyncio
import copy

from pymongo import ReturnDocument

from mybot.services.users import UserService


class FakeCollection:
    def __init__(self):
        self._documents: dict[int, dict] = {}

    def _resolve_field(self, document: dict, key: str) -> tuple[bool, object]:
        parts = key.split(".")
        current = document
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return False, None
            current = current[part]
        return True, current

    def _set_field(self, document: dict, key: str, value):
        parts = key.split(".")
        target = document
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = copy.deepcopy(value)

    def _matches(self, document: dict, criteria: dict) -> bool:
        for key, value in criteria.items():
            if key == "$or":
                return any(self._matches(document, option) for option in value)
            present, current = self._resolve_field(document, key)
            if isinstance(value, dict):
                if "$exists" in value:
                    exists = present
                    if value["$exists"] and not exists:
                        return False
                    if not value["$exists"] and exists:
                        return False
                    continue
                if not present or current != value:
                    return False
            else:
                if not present:
                    if value is None and not present:
                        # MongoDB treats missing fields as None for equality checks
                        continue
                    return False
                if current != value:
                    return False
        return True

    def _find_one(self, criteria: dict) -> dict | None:
        for document in self._documents.values():
            if self._matches(document, criteria):
                return copy.deepcopy(document)
        return None

    async def find_one(self, criteria: dict):
        result = self._find_one(criteria)
        return copy.deepcopy(result) if result is not None else None

    async def find_one_and_update(
        self,
        criteria: dict,
        update: dict,
        *,
        upsert: bool = False,
        return_document: ReturnDocument = ReturnDocument.AFTER,
    ):
        document = self._find_one(criteria)
        matched = document is not None
        if not matched and not upsert:
            return None
        if not matched:
            document = {}

        original = copy.deepcopy(document)

        if "$setOnInsert" in update and not matched:
            for key, value in update["$setOnInsert"].items():
                self._set_field(document, key, value)

        if "$set" in update:
            for key, value in update["$set"].items():
                self._set_field(document, key, value)

        if "$inc" in update:
            for key, value in update["$inc"].items():
                present, current = self._resolve_field(document, key)
                base = current if present else 0
                self._set_field(document, key, base + value)

        if not matched and upsert and "_id" not in document:
            if "_id" in criteria:
                document["_id"] = criteria["_id"]

        if "_id" not in document:
            raise ValueError("_id must be set on inserted documents")

        self._documents[document["_id"]] = document

        if return_document == ReturnDocument.AFTER:
            return copy.deepcopy(document)
        return copy.deepcopy(original)


class FakeDatabase:
    def __init__(self):
        self.users = FakeCollection()


def test_assign_referrer_sets_missing_value():
    database = FakeDatabase()
    service = UserService(database)

    user = asyncio.run(service.ensure_user(1, profile={"first_name": "Alice"}))
    assert user["referrer"] is None

    updated = asyncio.run(service.assign_referrer(1, 42))
    assert updated is not None
    assert updated["referrer"] == 42

    stored = asyncio.run(service.get(1))
    assert stored["referrer"] == 42


def test_assign_referrer_does_not_override_existing_value():
    database = FakeDatabase()
    service = UserService(database)

    asyncio.run(service.ensure_user(2, referrer=99))
    second = asyncio.run(service.assign_referrer(2, 123))
    assert second is None

    stored = asyncio.run(service.get(2))
    assert stored["referrer"] == 99

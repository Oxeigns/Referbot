"""Service layer protocol stubs and simple in-memory implementation for tests."""
from __future__ import annotations

from typing import Dict, List, Protocol


class Services(Protocol):
    def get_profile(self, user_id: int) -> Dict: ...

    def get_bot_username(self) -> str: ...

    def get_required_channels(self) -> List[Dict]: ...

    def get_verification_status(self, user_id: int) -> List[Dict]: ...

    def resolve_share_link(self, user_id: int) -> str: ...

    def get_leaderboard(self, page: int, size: int) -> Dict: ...

    def get_user_rank(self, user_id: int) -> Dict: ...

    def create_withdrawal(self, user_id: int, amount: int) -> Dict: ...

    def list_withdrawals(self, user_id: int, page: int, size: int) -> Dict: ...

    def is_owner(self, user_id: int) -> bool: ...


class MemoryServices:
    """Very small in-memory services used for unit tests."""

    def __init__(self):
        self.profiles: Dict[int, Dict] = {}
        self.withdrawals: List[Dict] = []
        self.bot_username = "referbot"

    def get_profile(self, user_id: int) -> Dict:
        return self.profiles.setdefault(
            user_id,
            {"points": 0, "refs": 0, "today": 0, "locale": "en", "eligible_withdraw": False},
        )

    def get_bot_username(self) -> str:
        return self.bot_username

    def get_required_channels(self) -> List[Dict]:
        return []

    def get_verification_status(self, user_id: int) -> List[Dict]:
        return []

    def resolve_share_link(self, user_id: int) -> str:
        return f"https://t.me/{self.bot_username}?start={user_id}"

    def get_leaderboard(self, page: int, size: int) -> Dict:
        return {"items": [], "total": 0}

    def get_user_rank(self, user_id: int) -> Dict:
        return {"rank": 0, "points": 0}

    def create_withdrawal(self, user_id: int, amount: int) -> Dict:
        record = {"id": str(len(self.withdrawals) + 1), "amount": amount, "status": "pending"}
        self.withdrawals.append(record)
        return record

    def list_withdrawals(self, user_id: int, page: int, size: int) -> Dict:
        start = (page - 1) * size
        items = self.withdrawals[start : start + size]
        return {"items": items, "total": len(self.withdrawals)}

    def is_owner(self, user_id: int) -> bool:
        return False

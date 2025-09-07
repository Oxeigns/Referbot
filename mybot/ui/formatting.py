"""Formatting helpers for messages."""
from __future__ import annotations

import html


def html_escape(text: str) -> str:
    """Escape text for safe HTML usage."""
    return html.escape(text or "")


def username_short(name: str, max_length: int = 20) -> str:
    """Shorten a username preserving ellipsis if needed."""
    if len(name) <= max_length:
        return name
    return name[: max_length - 1] + "…"


def points_fmt(points: int) -> str:
    """Format points as string."""
    return f"{points}"

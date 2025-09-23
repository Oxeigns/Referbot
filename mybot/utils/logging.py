"""Logging helpers."""

from __future__ import annotations

import logging
from typing import Any


def setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level, logging.INFO))


def censor(value: Any) -> str:
    text = str(value)
    if len(text) <= 4:
        return "***"
    return f"{text[:2]}***{text[-2:]}"

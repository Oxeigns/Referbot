"""Simple JSON-based i18n loader."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

BASE_PATH = Path(__file__).resolve().parent / "strings"
DEFAULT_LOCALE = "en"


@lru_cache(maxsize=None)
def load_bundle(locale: str) -> Dict[str, str]:
    """Load translation bundle for a locale.

    Falls back to English bundle when the requested locale is missing.
    """
    path = BASE_PATH / f"{locale}.json"
    if not path.exists() and locale != DEFAULT_LOCALE:
        path = BASE_PATH / f"{DEFAULT_LOCALE}.json"
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def t(key: str, locale: str = DEFAULT_LOCALE, **kwargs: Any) -> str:
    """Translate key for given locale with formatting.

    Unknown keys or locales fall back to English or return the key itself.
    """
    bundle = load_bundle(locale)
    if key not in bundle:
        bundle = load_bundle(DEFAULT_LOCALE)
    text = bundle.get(key, key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text

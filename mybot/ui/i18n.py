"""Simple JSON based internationalisation helper."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(slots=True)
class Translator:
    catalogues: Dict[str, Dict[str, Any]]
    default_locale: str = "en"

    @classmethod
    def from_path(cls, path: Path, *, default_locale: str = "en") -> "Translator":
        catalogues: Dict[str, Dict[str, Any]] = {}
        for file in path.glob("*.json"):
            with file.open("r", encoding="utf-8") as fh:
                catalogues[file.stem] = json.load(fh)
        if default_locale not in catalogues:
            raise RuntimeError(f"Missing default locale bundle: {default_locale}")
        return cls(catalogues=catalogues, default_locale=default_locale)

    def t(self, key: str, *, locale: str | None = None, **kwargs: Any) -> str:
        locale = locale or self.default_locale
        parts = key.split(".")
        catalogue = self.catalogues.get(locale, self.catalogues[self.default_locale])
        value: Any = catalogue
        for part in parts:
            value = value.get(part)
            if value is None:
                break
        if value is None:
            value = self.catalogues[self.default_locale]
            for part in parts:
                value = value.get(part)
                if value is None:
                    raise KeyError(key)
        if isinstance(value, str):
            return value.format(**kwargs)
        raise TypeError(f"Translation for {key} is not a string")

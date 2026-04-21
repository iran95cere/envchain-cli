"""Per-variable annotation support for envchain profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json
import os


@dataclass
class Annotation:
    var_name: str
    note: str
    author: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "var_name": self.var_name,
            "note": self.note,
            "author": self.author,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Annotation":
        return cls(
            var_name=data["var_name"],
            note=data["note"],
            author=data.get("author", ""),
            created_at=data.get("created_at", ""),
        )

    def __repr__(self) -> str:
        return f"Annotation(var={self.var_name!r}, note={self.note!r}, author={self.author!r})"


class AnnotationManager:
    """Stores and retrieves annotations for a given profile."""

    def __init__(self, storage_dir: str, profile_name: str) -> None:
        self._path = os.path.join(storage_dir, f"{profile_name}.annotations.json")
        self._data: Dict[str, Annotation] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self._data = {k: Annotation.from_dict(v) for k, v in raw.items()}

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump({k: v.to_dict() for k, v in self._data.items()}, fh, indent=2)

    def add(self, var_name: str, note: str, author: str = "") -> Annotation:
        ann = Annotation(var_name=var_name, note=note, author=author)
        self._data[var_name] = ann
        self._save()
        return ann

    def remove(self, var_name: str) -> bool:
        if var_name in self._data:
            del self._data[var_name]
            self._save()
            return True
        return False

    def get(self, var_name: str) -> Optional[Annotation]:
        return self._data.get(var_name)

    def all(self) -> List[Annotation]:
        return list(self._data.values())

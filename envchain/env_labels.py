"""Label management for environment variable profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LabelEntry:
    var_name: str
    label: str
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "var_name": self.var_name,
            "label": self.label,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LabelEntry":
        return cls(
            var_name=data["var_name"],
            label=data["label"],
            description=data.get("description", ""),
        )

    def __repr__(self) -> str:
        return f"LabelEntry(var={self.var_name!r}, label={self.label!r})"


class LabelManager:
    """Manage human-readable labels for environment variables."""

    def __init__(self) -> None:
        self._entries: Dict[str, LabelEntry] = {}

    def add(self, var_name: str, label: str, description: str = "") -> LabelEntry:
        if not var_name:
            raise ValueError("var_name must not be empty")
        if not label:
            raise ValueError("label must not be empty")
        entry = LabelEntry(var_name=var_name, label=label, description=description)
        self._entries[var_name] = entry
        return entry

    def remove(self, var_name: str) -> bool:
        if var_name in self._entries:
            del self._entries[var_name]
            return True
        return False

    def get(self, var_name: str) -> Optional[LabelEntry]:
        return self._entries.get(var_name)

    def all_entries(self) -> List[LabelEntry]:
        return list(self._entries.values())

    def labeled_vars(self, label: str) -> List[str]:
        """Return all var names that carry the given label (case-insensitive)."""
        label_lower = label.lower()
        return [
            e.var_name for e in self._entries.values()
            if e.label.lower() == label_lower
        ]

    def to_dict(self) -> dict:
        return {k: v.to_dict() for k, v in self._entries.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "LabelManager":
        mgr = cls()
        for entry_data in data.values():
            entry = LabelEntry.from_dict(entry_data)
            mgr._entries[entry.var_name] = entry
        return mgr

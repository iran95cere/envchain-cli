"""Tracks a changelog of variable-level changes per profile."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ChangeEntry:
    profile: str
    var_name: str
    action: str          # 'set', 'delete', 'rename'
    old_value: Optional[str]
    new_value: Optional[str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "var_name": self.var_name,
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChangeEntry":
        return cls(
            profile=data["profile"],
            var_name=data["var_name"],
            action=data["action"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            timestamp=data.get("timestamp", 0.0),
        )

    def __repr__(self) -> str:
        return (
            f"ChangeEntry(profile={self.profile!r}, var={self.var_name!r},"
            f" action={self.action!r})"
        )


VALID_ACTIONS = {"set", "delete", "rename"}


class ChangelogManager:
    def __init__(self, storage_dir: str) -> None:
        self._path = Path(storage_dir) / "changelog.json"
        self._entries: List[ChangeEntry] = self._load()

    def _load(self) -> List[ChangeEntry]:
        if not self._path.exists():
            return []
        try:
            raw = json.loads(self._path.read_text())
            return [ChangeEntry.from_dict(e) for e in raw]
        except (json.JSONDecodeError, KeyError):
            return []

    def _save(self) -> None:
        self._path.write_text(json.dumps([e.to_dict() for e in self._entries], indent=2))

    def record(self, profile: str, var_name: str, action: str,
               old_value: Optional[str] = None, new_value: Optional[str] = None) -> ChangeEntry:
        if action not in VALID_ACTIONS:
            raise ValueError(f"Invalid action {action!r}. Must be one of {VALID_ACTIONS}")
        entry = ChangeEntry(profile=profile, var_name=var_name, action=action,
                            old_value=old_value, new_value=new_value)
        self._entries.append(entry)
        self._save()
        return entry

    def entries_for_profile(self, profile: str) -> List[ChangeEntry]:
        return [e for e in self._entries if e.profile == profile]

    def all_entries(self) -> List[ChangeEntry]:
        return list(self._entries)

    def clear(self, profile: Optional[str] = None) -> int:
        before = len(self._entries)
        if profile:
            self._entries = [e for e in self._entries if e.profile != profile]
        else:
            self._entries = []
        self._save()
        return before - len(self._entries)

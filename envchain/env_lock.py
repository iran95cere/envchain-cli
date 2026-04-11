"""Profile locking — prevent accidental writes to a profile."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class LockEntry:
    profile: str
    locked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str = ""

    def to_dict(self) -> dict:
        return {"profile": self.profile, "locked_at": self.locked_at, "reason": self.reason}

    @classmethod
    def from_dict(cls, data: dict) -> "LockEntry":
        return cls(
            profile=data["profile"],
            locked_at=data.get("locked_at", ""),
            reason=data.get("reason", ""),
        )

    def __repr__(self) -> str:
        return f"LockEntry(profile={self.profile!r}, locked_at={self.locked_at!r})"


class LockManager:
    """Persist and query profile lock state."""

    def __init__(self, storage_dir: str) -> None:
        self._path = Path(storage_dir) / ".locks.json"
        self._locks: dict[str, LockEntry] = self._load()

    def _load(self) -> dict[str, LockEntry]:
        if not self._path.exists():
            return {}
        try:
            raw = json.loads(self._path.read_text())
            return {k: LockEntry.from_dict(v) for k, v in raw.items()}
        except (json.JSONDecodeError, KeyError):
            return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps({k: v.to_dict() for k, v in self._locks.items()}, indent=2))

    def lock(self, profile: str, reason: str = "") -> LockEntry:
        entry = LockEntry(profile=profile, reason=reason)
        self._locks[profile] = entry
        self._save()
        return entry

    def unlock(self, profile: str) -> bool:
        if profile not in self._locks:
            return False
        del self._locks[profile]
        self._save()
        return True

    def is_locked(self, profile: str) -> bool:
        return profile in self._locks

    def get_entry(self, profile: str) -> Optional[LockEntry]:
        return self._locks.get(profile)

    def list_locked(self) -> List[LockEntry]:
        return list(self._locks.values())

"""Tracks the history of changes made to environment variable profiles."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class HistoryEntry:
    profile: str
    action: str  # 'set', 'remove', 'init'
    key: Optional[str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            "profile": self.profile,
            "action": self.action,
            "key": self.key,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "HistoryEntry":
        return cls(
            profile=data["profile"],
            action=data["action"],
            key=data.get("key"),
            timestamp=data["timestamp"],
        )

    def __repr__(self) -> str:
        return f"<HistoryEntry profile={self.profile!r} action={self.action!r} key={self.key!r}>"


class HistoryManager:
    def __init__(self, history_dir: Path) -> None:
        self._dir = Path(history_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, profile: str) -> Path:
        return self._dir / f"{profile}.history.json"

    def record(self, profile: str, action: str, key: Optional[str] = None) -> HistoryEntry:
        entry = HistoryEntry(profile=profile, action=action, key=key)
        entries = self.get_history(profile)
        entries.append(entry)
        self._path(profile).write_text(
            json.dumps([e.to_dict() for e in entries], indent=2)
        )
        return entry

    def get_history(self, profile: str) -> List[HistoryEntry]:
        path = self._path(profile)
        if not path.exists():
            return []
        data = json.loads(path.read_text())
        return [HistoryEntry.from_dict(d) for d in data]

    def clear_history(self, profile: str) -> None:
        path = self._path(profile)
        if path.exists():
            path.unlink()

    def last_entry(self, profile: str) -> Optional[HistoryEntry]:
        entries = self.get_history(profile)
        return entries[-1] if entries else None

"""Version tracking for environment variable profiles."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class VersionEntry:
    profile: str
    version: int
    timestamp: float
    author: str = ""
    message: str = ""
    snapshot: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "version": self.version,
            "timestamp": self.timestamp,
            "author": self.author,
            "message": self.message,
            "snapshot": dict(self.snapshot),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VersionEntry":
        return cls(
            profile=data["profile"],
            version=data["version"],
            timestamp=data["timestamp"],
            author=data.get("author", ""),
            message=data.get("message", ""),
            snapshot=data.get("snapshot", {}),
        )

    def __repr__(self) -> str:
        return (
            f"<VersionEntry profile={self.profile!r} "
            f"version={self.version} message={self.message!r}>"
        )


class VersionManager:
    """Tracks version history for a profile's environment variables."""

    def __init__(self, storage_dir: str, profile: str) -> None:
        import json
        import os

        self._json = json
        self._os = os
        self._path = os.path.join(storage_dir, f"{profile}.versions.json")
        self._profile = profile
        self._entries: List[VersionEntry] = self._load()

    def _load(self) -> List[VersionEntry]:
        if not self._os.path.exists(self._path):
            return []
        with open(self._path, "r") as fh:
            raw = self._json.load(fh)
        return [VersionEntry.from_dict(d) for d in raw]

    def _save(self) -> None:
        with open(self._path, "w") as fh:
            self._json.dump([e.to_dict() for e in self._entries], fh, indent=2)

    def commit(
        self,
        vars_snapshot: Dict[str, str],
        message: str = "",
        author: str = "",
    ) -> VersionEntry:
        next_version = (self._entries[-1].version + 1) if self._entries else 1
        entry = VersionEntry(
            profile=self._profile,
            version=next_version,
            timestamp=time.time(),
            author=author,
            message=message,
            snapshot=dict(vars_snapshot),
        )
        self._entries.append(entry)
        self._save()
        return entry

    def history(self) -> List[VersionEntry]:
        return list(self._entries)

    def get(self, version: int) -> Optional[VersionEntry]:
        for e in self._entries:
            if e.version == version:
                return e
        return None

    def latest(self) -> Optional[VersionEntry]:
        return self._entries[-1] if self._entries else None

    def clear(self) -> None:
        self._entries = []
        self._save()

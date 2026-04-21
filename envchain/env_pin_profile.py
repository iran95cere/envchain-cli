"""Pin a profile to a specific directory or working context."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PinProfileEntry:
    profile: str
    directory: str
    created_at: str

    def to_dict(self) -> Dict:
        return {
            "profile": self.profile,
            "directory": self.directory,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PinProfileEntry":
        return cls(
            profile=data["profile"],
            directory=data["directory"],
            created_at=data.get("created_at", ""),
        )

    def __repr__(self) -> str:
        return f"PinProfileEntry(profile={self.profile!r}, directory={self.directory!r})"


class PinProfileManager:
    _FILENAME = "pin_profile.json"

    def __init__(self, storage_dir: str) -> None:
        self._path = Path(storage_dir) / self._FILENAME
        self._entries: Dict[str, PinProfileEntry] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            data = json.loads(self._path.read_text())
            self._entries = {
                k: PinProfileEntry.from_dict(v) for k, v in data.items()
            }

    def _save(self) -> None:
        self._path.write_text(
            json.dumps({k: v.to_dict() for k, v in self._entries.items()}, indent=2)
        )

    def pin(self, directory: str, profile: str) -> PinProfileEntry:
        import datetime
        entry = PinProfileEntry(
            profile=profile,
            directory=str(Path(directory).resolve()),
            created_at=datetime.datetime.utcnow().isoformat(),
        )
        self._entries[entry.directory] = entry
        self._save()
        return entry

    def unpin(self, directory: str) -> bool:
        key = str(Path(directory).resolve())
        if key in self._entries:
            del self._entries[key]
            self._save()
            return True
        return False

    def resolve(self, directory: str) -> Optional[str]:
        """Return the pinned profile for the given directory, or None."""
        key = str(Path(directory).resolve())
        entry = self._entries.get(key)
        return entry.profile if entry else None

    def list_pins(self) -> List[PinProfileEntry]:
        return list(self._entries.values())

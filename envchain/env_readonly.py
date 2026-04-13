"""Read-only variable protection for environment profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class ReadOnlyEntry:
    var_name: str
    profile: str
    locked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "var_name": self.var_name,
            "profile": self.profile,
            "locked_at": self.locked_at,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReadOnlyEntry":
        return cls(
            var_name=data["var_name"],
            profile=data["profile"],
            locked_at=data.get("locked_at", datetime.now(timezone.utc).isoformat()),
            reason=data.get("reason"),
        )

    def __repr__(self) -> str:
        reason_part = f", reason={self.reason!r}" if self.reason else ""
        return f"ReadOnlyEntry(var={self.var_name!r}, profile={self.profile!r}{reason_part})"


class ReadOnlyViolation(Exception):
    """Raised when attempting to modify a read-only variable."""


class ReadOnlyManager:
    def __init__(self, storage_dir: str):
        import json
        import os
        self._path = os.path.join(storage_dir, "readonly.json")
        self._json = json
        self._os = os
        self._entries: Dict[str, Dict[str, ReadOnlyEntry]] = {}
        self._load()

    def _load(self) -> None:
        if not self._os.path.exists(self._path):
            return
        with open(self._path, "r") as fh:
            raw = self._json.load(fh)
        for profile, vars_ in raw.items():
            self._entries[profile] = {
                k: ReadOnlyEntry.from_dict(v) for k, v in vars_.items()
            }

    def _save(self) -> None:
        raw = {
            profile: {k: e.to_dict() for k, e in vars_.items()}
            for profile, vars_ in self._entries.items()
        }
        with open(self._path, "w") as fh:
            self._json.dump(raw, fh, indent=2)

    def protect(self, profile: str, var_name: str, reason: Optional[str] = None) -> ReadOnlyEntry:
        entry = ReadOnlyEntry(var_name=var_name, profile=profile, reason=reason)
        self._entries.setdefault(profile, {})[var_name] = entry
        self._save()
        return entry

    def unprotect(self, profile: str, var_name: str) -> bool:
        removed = self._entries.get(profile, {}).pop(var_name, None)
        if removed:
            self._save()
        return removed is not None

    def is_protected(self, profile: str, var_name: str) -> bool:
        return var_name in self._entries.get(profile, {})

    def assert_writable(self, profile: str, var_name: str) -> None:
        if self.is_protected(profile, var_name):
            raise ReadOnlyViolation(
                f"Variable '{var_name}' in profile '{profile}' is read-only."
            )

    def list_protected(self, profile: str) -> List[ReadOnlyEntry]:
        return list(self._entries.get(profile, {}).values())

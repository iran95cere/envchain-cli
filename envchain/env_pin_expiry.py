"""Pin expiry management: track when per-profile pins expire and surface warnings."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class PinExpiryEntry:
    profile: str
    expires_at: datetime  # UTC

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    def seconds_remaining(self) -> float:
        delta = (self.expires_at - datetime.now(timezone.utc)).total_seconds()
        return max(0.0, delta)

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PinExpiryEntry":
        return cls(
            profile=data["profile"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )

    def __repr__(self) -> str:
        status = "expired" if self.is_expired() else f"{self.seconds_remaining():.0f}s remaining"
        return f"<PinExpiryEntry profile={self.profile!r} {status}>"


class PinExpiryManager:
    _FILENAME = "pin_expiry.json"

    def __init__(self, storage_dir: str) -> None:
        self._path = os.path.join(storage_dir, self._FILENAME)
        self._entries: Dict[str, PinExpiryEntry] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        for item in raw:
            entry = PinExpiryEntry.from_dict(item)
            self._entries[entry.profile] = entry

    def _save(self) -> None:
        data = [e.to_dict() for e in self._entries.values()]
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def set_expiry(self, profile: str, expires_at: datetime) -> PinExpiryEntry:
        entry = PinExpiryEntry(profile=profile, expires_at=expires_at)
        self._entries[profile] = entry
        self._save()
        return entry

    def get_expiry(self, profile: str) -> Optional[PinExpiryEntry]:
        return self._entries.get(profile)

    def remove_expiry(self, profile: str) -> bool:
        if profile in self._entries:
            del self._entries[profile]
            self._save()
            return True
        return False

    def expired_profiles(self) -> List[PinExpiryEntry]:
        return [e for e in self._entries.values() if e.is_expired()]

    def all_entries(self) -> List[PinExpiryEntry]:
        return list(self._entries.values())

"""Time-to-live (TTL) management for environment variable profiles."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class TTLEntry:
    profile_name: str
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    def seconds_remaining(self) -> float:
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0.0, delta.total_seconds())

    def to_dict(self) -> dict:
        return {
            "profile_name": self.profile_name,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TTLEntry":
        return cls(
            profile_name=data["profile_name"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def __repr__(self) -> str:
        status = "expired" if self.is_expired() else f"{self.seconds_remaining():.0f}s remaining"
        return f"<TTLEntry profile={self.profile_name!r} {status}>"


class TTLManager:
    _FILENAME = "ttl_index.json"

    def __init__(self, storage_dir: str) -> None:
        self._path = os.path.join(storage_dir, self._FILENAME)
        self._entries: Dict[str, TTLEntry] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        self._entries = {k: TTLEntry.from_dict(v) for k, v in raw.items()}

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump({k: v.to_dict() for k, v in self._entries.items()}, fh, indent=2)

    def set_ttl(self, profile_name: str, seconds: float) -> TTLEntry:
        if seconds <= 0:
            raise ValueError("TTL must be a positive number of seconds.")
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        entry = TTLEntry(profile_name=profile_name, expires_at=expires_at)
        self._entries[profile_name] = entry
        self._save()
        return entry

    def get_ttl(self, profile_name: str) -> Optional[TTLEntry]:
        return self._entries.get(profile_name)

    def remove_ttl(self, profile_name: str) -> bool:
        if profile_name in self._entries:
            del self._entries[profile_name]
            self._save()
            return True
        return False

    def expired_profiles(self) -> List[str]:
        return [name for name, entry in self._entries.items() if entry.is_expired()]

    def purge_expired(self) -> List[str]:
        expired = self.expired_profiles()
        for name in expired:
            del self._entries[name]
        if expired:
            self._save()
        return expired

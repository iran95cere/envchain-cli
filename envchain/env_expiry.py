"""Variable expiry management for envchain profiles."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExpiryEntry:
    var_name: str
    profile: str
    expires_at: float  # Unix timestamp
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    def seconds_remaining(self) -> float:
        return max(0.0, self.expires_at - time.time())

    def to_dict(self) -> dict:
        return {
            "var_name": self.var_name,
            "profile": self.profile,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExpiryEntry":
        return cls(
            var_name=data["var_name"],
            profile=data["profile"],
            expires_at=data["expires_at"],
            created_at=data.get("created_at", time.time()),
        )

    def __repr__(self) -> str:
        status = "expired" if self.is_expired() else f"{self.seconds_remaining():.1f}s remaining"
        return f"<ExpiryEntry {self.profile}/{self.var_name} [{status}]>"


class ExpiryManager:
    """Tracks and evaluates variable expiry entries."""

    def __init__(self) -> None:
        self._entries: Dict[str, ExpiryEntry] = {}  # key: "profile/var_name"

    def _key(self, profile: str, var_name: str) -> str:
        return f"{profile}/{var_name}"

    def set_expiry(self, profile: str, var_name: str, ttl_seconds: float) -> ExpiryEntry:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        entry = ExpiryEntry(
            var_name=var_name,
            profile=profile,
            expires_at=time.time() + ttl_seconds,
        )
        self._entries[self._key(profile, var_name)] = entry
        return entry

    def get_entry(self, profile: str, var_name: str) -> Optional[ExpiryEntry]:
        return self._entries.get(self._key(profile, var_name))

    def is_expired(self, profile: str, var_name: str) -> bool:
        entry = self.get_entry(profile, var_name)
        return entry is not None and entry.is_expired()

    def remove(self, profile: str, var_name: str) -> bool:
        key = self._key(profile, var_name)
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def expired_entries(self) -> List[ExpiryEntry]:
        return [e for e in self._entries.values() if e.is_expired()]

    def all_entries(self) -> List[ExpiryEntry]:
        return list(self._entries.values())

    def purge_expired(self) -> List[ExpiryEntry]:
        expired = self.expired_entries()
        for e in expired:
            self.remove(e.profile, e.var_name)
        return expired

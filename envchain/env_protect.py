"""Protection rules for environment variables — prevent accidental overwrite or deletion."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os


@dataclass
class ProtectEntry:
    profile: str
    var_name: str
    reason: str = ""

    def to_dict(self) -> dict:
        return {"profile": self.profile, "var_name": self.var_name, "reason": self.reason}

    @classmethod
    def from_dict(cls, data: dict) -> "ProtectEntry":
        return cls(
            profile=data["profile"],
            var_name=data["var_name"],
            reason=data.get("reason", ""),
        )

    def __repr__(self) -> str:
        return f"ProtectEntry(profile={self.profile!r}, var={self.var_name!r})"


@dataclass
class ProtectViolation:
    profile: str
    var_name: str
    action: str  # 'overwrite' | 'delete'

    def __repr__(self) -> str:
        return f"ProtectViolation({self.action} of {self.var_name!r} in {self.profile!r})"


class ProtectManager:
    def __init__(self, storage_dir: str) -> None:
        self._path = os.path.join(storage_dir, "_protect_index.json")
        self._entries: Dict[str, Dict[str, ProtectEntry]] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        for profile, vars_ in raw.items():
            self._entries[profile] = {
                k: ProtectEntry.from_dict(v) for k, v in vars_.items()
            }

    def _save(self) -> None:
        data = {
            profile: {k: e.to_dict() for k, e in vars_.items()}
            for profile, vars_ in self._entries.items()
        }
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def protect(self, profile: str, var_name: str, reason: str = "") -> ProtectEntry:
        self._entries.setdefault(profile, {})
        entry = ProtectEntry(profile=profile, var_name=var_name, reason=reason)
        self._entries[profile][var_name] = entry
        self._save()
        return entry

    def unprotect(self, profile: str, var_name: str) -> bool:
        removed = bool(self._entries.get(profile, {}).pop(var_name, None))
        if removed:
            self._save()
        return removed

    def is_protected(self, profile: str, var_name: str) -> bool:
        return var_name in self._entries.get(profile, {})

    def list_protected(self, profile: str) -> List[ProtectEntry]:
        return list(self._entries.get(profile, {}).values())

    def check_overwrite(self, profile: str, var_name: str) -> Optional[ProtectViolation]:
        if self.is_protected(profile, var_name):
            return ProtectViolation(profile=profile, var_name=var_name, action="overwrite")
        return None

    def check_delete(self, profile: str, var_name: str) -> Optional[ProtectViolation]:
        if self.is_protected(profile, var_name):
            return ProtectViolation(profile=profile, var_name=var_name, action="delete")
        return None

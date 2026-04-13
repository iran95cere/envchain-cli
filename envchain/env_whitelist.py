"""Whitelist management for allowed environment variable names per profile."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WhitelistViolation:
    var_name: str
    profile: str

    def __repr__(self) -> str:
        return f"<WhitelistViolation var={self.var_name!r} profile={self.profile!r}>"


@dataclass
class WhitelistReport:
    violations: List[WhitelistViolation] = field(default_factory=list)
    checked: int = 0

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def has_violations(self) -> bool:
        return bool(self.violations)

    def __repr__(self) -> str:
        return (
            f"<WhitelistReport checked={self.checked} violations={self.violation_count}>"
        )


class WhitelistManager:
    """Persist and enforce per-profile variable name whitelists."""

    def __init__(self, storage_dir: str) -> None:
        self._path = os.path.join(storage_dir, "whitelists.json")
        self._data: Dict[str, List[str]] = self._load()

    def _load(self) -> Dict[str, List[str]]:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    def add(self, profile: str, var_name: str) -> None:
        """Add *var_name* to the whitelist for *profile*."""
        if not var_name:
            raise ValueError("var_name must not be empty")
        self._data.setdefault(profile, [])
        if var_name not in self._data[profile]:
            self._data[profile].append(var_name)
            self._save()

    def remove(self, profile: str, var_name: str) -> bool:
        """Remove *var_name* from the whitelist. Returns True if it was present."""
        names = self._data.get(profile, [])
        if var_name in names:
            names.remove(var_name)
            self._data[profile] = names
            self._save()
            return True
        return False

    def get(self, profile: str) -> List[str]:
        """Return the whitelist for *profile* (empty list if none defined)."""
        return list(self._data.get(profile, []))

    def is_enabled(self, profile: str) -> bool:
        """A whitelist is considered enabled when at least one entry exists."""
        return bool(self._data.get(profile))

    def check(self, profile: str, vars_dict: Dict[str, str]) -> WhitelistReport:
        """Validate *vars_dict* keys against the whitelist for *profile*."""
        report = WhitelistReport(checked=len(vars_dict))
        if not self.is_enabled(profile):
            return report
        allowed = set(self._data[profile])
        for name in vars_dict:
            if name not in allowed:
                report.violations.append(WhitelistViolation(var_name=name, profile=profile))
        return report

"""Track and report deprecated environment variable names."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class DeprecationEntry:
    var_name: str
    replacement: Optional[str]
    reason: str
    deprecated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "var_name": self.var_name,
            "replacement": self.replacement,
            "reason": self.reason,
            "deprecated_at": self.deprecated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeprecationEntry":
        return cls(
            var_name=data["var_name"],
            replacement=data.get("replacement"),
            reason=data.get("reason", ""),
            deprecated_at=data.get("deprecated_at", datetime.utcnow().isoformat()),
        )

    def __repr__(self) -> str:
        repl = f" -> {self.replacement}" if self.replacement else ""
        return f"<DeprecationEntry {self.var_name}{repl}>"


@dataclass
class DeprecationReport:
    entries: List[DeprecationEntry] = field(default_factory=list)
    checked_vars: List[str] = field(default_factory=list)

    @property
    def deprecated_count(self) -> int:
        return len(self.entries)

    @property
    def has_deprecated(self) -> bool:
        return len(self.entries) > 0

    def __repr__(self) -> str:
        return f"<DeprecationReport deprecated={self.deprecated_count} checked={len(self.checked_vars)}>"


class DeprecationChecker:
    """Check profile variables against a registry of deprecated names."""

    def __init__(self) -> None:
        self._registry: Dict[str, DeprecationEntry] = {}

    def register(self, var_name: str, reason: str, replacement: Optional[str] = None) -> None:
        if not var_name:
            raise ValueError("var_name must not be empty")
        self._registry[var_name.upper()] = DeprecationEntry(
            var_name=var_name.upper(),
            replacement=replacement.upper() if replacement else None,
            reason=reason,
        )

    def unregister(self, var_name: str) -> bool:
        return self._registry.pop(var_name.upper(), None) is not None

    def check(self, variables: Dict[str, str]) -> DeprecationReport:
        entries: List[DeprecationEntry] = []
        checked = list(variables.keys())
        for name in checked:
            entry = self._registry.get(name.upper())
            if entry:
                entries.append(entry)
        return DeprecationReport(entries=entries, checked_vars=checked)

    def all_deprecated(self) -> List[DeprecationEntry]:
        return list(self._registry.values())

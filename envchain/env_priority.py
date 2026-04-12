"""Priority-based variable resolution across multiple profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PriorityEntry:
    """A variable resolved from a specific profile at a given priority level."""

    var_name: str
    value: str
    profile: str
    priority: int

    def to_dict(self) -> dict:
        return {
            "var_name": self.var_name,
            "value": self.value,
            "profile": self.profile,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PriorityEntry":
        return cls(
            var_name=data["var_name"],
            value=data["value"],
            profile=data["profile"],
            priority=data["priority"],
        )

    def __repr__(self) -> str:
        return (
            f"PriorityEntry(var={self.var_name!r}, profile={self.profile!r},"
            f" priority={self.priority})"
        )


@dataclass
class PriorityResult:
    """Result of a priority-based resolution pass."""

    resolved: Dict[str, PriorityEntry] = field(default_factory=dict)
    conflicts: Dict[str, List[PriorityEntry]] = field(default_factory=dict)

    @property
    def var_count(self) -> int:
        return len(self.resolved)

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def to_flat_dict(self) -> Dict[str, str]:
        return {name: entry.value for name, entry in self.resolved.items()}

    def __repr__(self) -> str:
        return (
            f"PriorityResult(vars={self.var_count}, conflicts={self.conflict_count})"
        )


class EnvPriority:
    """Resolves environment variables from multiple profiles using priority order."""

    def resolve(
        self,
        profiles: List[Tuple[str, Dict[str, str], int]],
        track_conflicts: bool = False,
    ) -> PriorityResult:
        """Resolve variables from (profile_name, vars_dict, priority) tuples.

        Higher priority value wins. When priorities are equal the first
        profile listed wins (stable).
        """
        result = PriorityResult()
        seen: Dict[str, List[PriorityEntry]] = {}

        for profile_name, vars_dict, priority in profiles:
            for var_name, value in vars_dict.items():
                entry = PriorityEntry(
                    var_name=var_name,
                    value=value,
                    profile=profile_name,
                    priority=priority,
                )
                seen.setdefault(var_name, []).append(entry)

        for var_name, entries in seen.items():
            winner = max(entries, key=lambda e: e.priority)
            result.resolved[var_name] = winner
            if track_conflicts and len(entries) > 1:
                losers = [e for e in entries if e is not winner]
                if losers:
                    result.conflicts[var_name] = entries

        return result

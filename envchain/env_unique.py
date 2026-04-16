"""Detect and report variables with unique vs. shared values across profiles."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class UniqueEntry:
    """Tracks which profiles contain a given variable name."""
    var_name: str
    profiles: List[str] = field(default_factory=list)

    @property
    def profile_count(self) -> int:
        return len(self.profiles)

    @property
    def is_unique(self) -> bool:
        """True when the variable appears in exactly one profile."""
        return self.profile_count == 1

    def __repr__(self) -> str:
        return f"UniqueEntry(var={self.var_name!r}, profiles={self.profiles})"

    def to_dict(self) -> dict:
        return {"var_name": self.var_name, "profiles": list(self.profiles)}

    @classmethod
    def from_dict(cls, data: dict) -> "UniqueEntry":
        return cls(var_name=data["var_name"], profiles=list(data.get("profiles", [])))


@dataclass
class UniqueReport:
    entries: List[UniqueEntry] = field(default_factory=list)

    @property
    def unique_vars(self) -> List[UniqueEntry]:
        return [e for e in self.entries if e.is_unique]

    @property
    def shared_vars(self) -> List[UniqueEntry]:
        return [e for e in self.entries if not e.is_unique]

    @property
    def unique_count(self) -> int:
        return len(self.unique_vars)

    @property
    def shared_count(self) -> int:
        return len(self.shared_vars)

    def __repr__(self) -> str:
        return (
            f"UniqueReport(unique={self.unique_count}, shared={self.shared_count})"
        )


class EnvUniqueness:
    """Analyse variable name uniqueness across multiple profiles."""

    def analyse(self, profiles: Dict[str, Dict[str, str]]) -> UniqueReport:
        """Return a UniqueReport for the given mapping of profile_name -> vars."""
        var_to_profiles: Dict[str, List[str]] = {}
        for profile_name, vars_ in profiles.items():
            for var_name in vars_:
                var_to_profiles.setdefault(var_name, []).append(profile_name)

        entries = [
            UniqueEntry(var_name=var, profiles=sorted(profs))
            for var, profs in sorted(var_to_profiles.items())
        ]
        return UniqueReport(entries=entries)

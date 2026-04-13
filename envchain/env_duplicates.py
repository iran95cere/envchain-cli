"""Detect duplicate values across variables within a profile or across profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DuplicateGroup:
    """A group of variable names that share the same value."""

    value: str
    names: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"DuplicateGroup(value=***, names={self.names})"

    def to_dict(self) -> dict:
        return {"value": self.value, "names": list(self.names)}

    @classmethod
    def from_dict(cls, data: dict) -> "DuplicateGroup":
        return cls(value=data["value"], names=list(data.get("names", [])))


@dataclass
class DuplicateReport:
    """Report of duplicate values found in a variable set."""

    profile: str
    groups: List[DuplicateGroup] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.groups) > 0

    @property
    def duplicate_count(self) -> int:
        """Total number of variables involved in duplicates."""
        return sum(len(g.names) for g in self.groups)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DuplicateReport(profile={self.profile!r}, "
            f"groups={len(self.groups)}, vars={self.duplicate_count})"
        )


class DuplicateDetector:
    """Detect variables that share identical values within a profile."""

    def detect(self, profile: str, variables: Dict[str, str]) -> DuplicateReport:
        """Return a DuplicateReport for the given variable mapping."""
        value_map: Dict[str, List[str]] = {}
        for name, value in variables.items():
            value_map.setdefault(value, []).append(name)

        groups = [
            DuplicateGroup(value=val, names=sorted(names))
            for val, names in value_map.items()
            if len(names) > 1
        ]
        groups.sort(key=lambda g: g.names[0])
        return DuplicateReport(profile=profile, groups=groups)

    def detect_across(
        self, profiles: Dict[str, Dict[str, str]]
    ) -> List[Tuple[str, str, List[str]]]:
        """Find (value, var_name) pairs shared across multiple profiles.

        Returns list of (value, var_name, [profile, ...]) tuples where the
        same variable name has the same value in more than one profile.
        """
        # key: (var_name, value) -> list of profile names
        mapping: Dict[Tuple[str, str], List[str]] = {}
        for profile_name, variables in profiles.items():
            for var_name, value in variables.items():
                mapping.setdefault((var_name, value), []).append(profile_name)

        results = [
            (value, var_name, sorted(profile_list))
            for (var_name, value), profile_list in mapping.items()
            if len(profile_list) > 1
        ]
        results.sort(key=lambda t: (t[1], t[0]))
        return results

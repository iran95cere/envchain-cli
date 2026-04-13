"""Cross-reference detection for environment variables across profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CrossRefEntry:
    """A variable name found in multiple profiles."""

    name: str
    profiles: List[str] = field(default_factory=list)

    def profile_count(self) -> int:
        return len(self.profiles)

    def __repr__(self) -> str:
        return f"<CrossRefEntry name={self.name!r} profiles={self.profiles}>"

    def to_dict(self) -> dict:
        return {"name": self.name, "profiles": list(self.profiles)}

    @classmethod
    def from_dict(cls, data: dict) -> "CrossRefEntry":
        return cls(name=data["name"], profiles=list(data.get("profiles", [])))


@dataclass
class CrossRefReport:
    """Report of cross-referenced variables across profiles."""

    entries: List[CrossRefEntry] = field(default_factory=list)

    @property
    def ref_count(self) -> int:
        return len(self.entries)

    @property
    def has_refs(self) -> bool:
        return bool(self.entries)

    def names(self) -> List[str]:
        return [e.name for e in self.entries]

    def __repr__(self) -> str:
        return f"<CrossRefReport entries={self.ref_count}>"


class EnvCrossRef:
    """Detect variables shared across multiple profiles."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def analyse(self, profile_names: Optional[List[str]] = None) -> CrossRefReport:
        """Return variables that appear in more than one profile."""
        names = profile_names or self._storage.list_profiles()
        var_map[str]] = {}
        for pname in names:
            profile = self._storage.load_profile(pname)
            if profile is None:
                continue
            forname in profile.vars:
                var_map.setdefault(var_name, []).append(pname)
        entries = [
            CrossRefEntry(name=k, profiles=v)
            for k, v in sorted(var_map.items())
            if len(v) > 1
        ]
        return CrossRefReport(entries=entries)

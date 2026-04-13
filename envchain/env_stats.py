"""Statistics and summary reporting for environment profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProfileStats:
    """Statistics for a single profile."""
    profile_name: str
    var_count: int = 0
    empty_value_count: int = 0
    longest_key: Optional[str] = None
    shortest_key: Optional[str] = None
    avg_value_length: float = 0.0
    key_prefixes: Dict[str, int] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"ProfileStats(profile={self.profile_name!r}, "
            f"vars={self.var_count}, empty={self.empty_value_count})"
        )

    def to_dict(self) -> dict:
        return {
            "profile_name": self.profile_name,
            "var_count": self.var_count,
            "empty_value_count": self.empty_value_count,
            "longest_key": self.longest_key,
            "shortest_key": self.shortest_key,
            "avg_value_length": self.avg_value_length,
            "key_prefixes": self.key_prefixes,
        }


class EnvStats:
    """Compute statistics over profile variable sets."""

    def compute(self, profile_name: str, variables: Dict[str, str]) -> ProfileStats:
        """Return a ProfileStats for the given variable mapping."""
        stats = ProfileStats(profile_name=profile_name)
        if not variables:
            return stats

        stats.var_count = len(variables)
        stats.empty_value_count = sum(1 for v in variables.values() if v == "")

        keys = list(variables.keys())
        stats.longest_key = max(keys, key=len)
        stats.shortest_key = min(keys, key=len)

        total_value_len = sum(len(v) for v in variables.values())
        stats.avg_value_length = total_value_len / stats.var_count

        prefix_counts: Dict[str, int] = {}
        for key in keys:
            prefix = key.split("_")[0] if "_" in key else key
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        stats.key_prefixes = prefix_counts

        return stats

    def summarise_many(self, profiles: Dict[str, Dict[str, str]]) -> List[ProfileStats]:
        """Return stats for multiple profiles, sorted by profile name."""
        return [
            self.compute(name, variables)
            for name, variables in sorted(profiles.items())
        ]

    def total_variable_count(self, profiles: Dict[str, Dict[str, str]]) -> int:
        """Return the total number of variables across all profiles.

        Duplicate keys that appear in multiple profiles are counted once
        per profile, reflecting actual storage rather than unique keys.
        """
        return sum(len(variables) for variables in profiles.values())

    def find_duplicate_keys(self, profiles: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
        """Return keys that appear in more than one profile.

        Returns a mapping of key -> list of profile names that define it.
        Only keys present in two or more profiles are included.
        """
        key_to_profiles: Dict[str, List[str]] = {}
        for profile_name, variables in profiles.items():
            for key in variables:
                key_to_profiles.setdefault(key, []).append(profile_name)
        return {key: names for key, names in key_to_profiles.items() if len(names) > 1}

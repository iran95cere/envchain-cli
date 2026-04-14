"""Condense environment variable sets by removing redundant/duplicate entries across profiles."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CondenseResult:
    name: str
    original_count: int
    condensed_count: int
    removed: List[str] = field(default_factory=list)

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def is_changed(self) -> bool:
        return self.original_count != self.condensed_count

    def __repr__(self) -> str:
        return (
            f"CondenseResult(profile={self.name!r}, "
            f"original={self.original_count}, condensed={self.condensed_count})"
        )


@dataclass
class CondenseReport:
    results: List[CondenseResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.is_changed)

    @property
    def total_removed(self) -> int:
        return sum(r.removed_count for r in self.results)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0


class EnvCondenser:
    """Remove variables whose values are empty or duplicate keys (case-insensitive)."""

    def condense(
        self,
        profile_name: str,
        variables: Dict[str, str],
        strip_empty: bool = True,
        deduplicate_case: bool = True,
    ) -> Tuple[Dict[str, str], CondenseResult]:
        original = dict(variables)
        result: Dict[str, str] = {}
        removed: List[str] = []
        seen_lower: Dict[str, str] = {}

        for key, value in original.items():
            if strip_empty and value.strip() == "":
                removed.append(key)
                continue
            lower = key.lower()
            if deduplicate_case and lower in seen_lower:
                removed.append(key)
                continue
            seen_lower[lower] = key
            result[key] = value

        cr = CondenseResult(
            name=profile_name,
            original_count=len(original),
            condensed_count=len(result),
            removed=removed,
        )
        return result, cr

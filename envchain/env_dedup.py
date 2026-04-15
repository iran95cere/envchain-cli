"""Deduplication of environment variable values across a profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DedupGroup:
    """A group of variable names that share the same value."""

    value: str
    names: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"DedupGroup(names={self.names!r}, value={self.value!r})"

    def to_dict(self) -> dict:
        return {"value": self.value, "names": list(self.names)}

    @classmethod
    def from_dict(cls, data: dict) -> "DedupGroup":
        return cls(value=data["value"], names=list(data.get("names", [])))


@dataclass
class DedupReport:
    """Report produced by EnvDeduplicator."""

    groups: List[DedupGroup] = field(default_factory=list)

    @property
    def duplicate_count(self) -> int:
        """Total number of variables that are duplicates (excluding the first occurrence)."""
        return sum(max(len(g.names) - 1, 0) for g in self.groups)

    @property
    def has_duplicates(self) -> bool:
        return self.duplicate_count > 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DedupReport(groups={len(self.groups)}, "
            f"duplicate_count={self.duplicate_count})"
        )


class EnvDeduplicator:
    """Detect and optionally remove duplicate values in a variable dict."""

    def analyse(self, variables: Dict[str, str]) -> DedupReport:
        """Return a DedupReport identifying variables that share identical values."""
        value_map: Dict[str, List[str]] = {}
        for name, value in variables.items():
            value_map.setdefault(value, []).append(name)

        groups = [
            DedupGroup(value=val, names=names)
            for val, names in value_map.items()
            if len(names) > 1
        ]
        return DedupReport(groups=groups)

    def remove_duplicates(
        self,
        variables: Dict[str, str],
        keep: str = "first",
        report: Optional[DedupReport] = None,
    ) -> Dict[str, str]:
        """Return a new dict with duplicate-value entries removed.

        Args:
            variables: Original variable mapping.
            keep: ``'first'`` keeps the alphabetically first name per group;
                  ``'last'`` keeps the alphabetically last name.
            report: Pre-computed DedupReport; if None, analyse() is called.
        """
        if report is None:
            report = self.analyse(variables)

        to_remove: set = set()
        for group in report.groups:
            sorted_names = sorted(group.names)
            if keep == "last":
                to_remove.update(sorted_names[:-1])
            else:
                to_remove.update(sorted_names[1:])

        return {k: v for k, v in variables.items() if k not in to_remove}

"""Namespace support for grouping environment variables by prefix convention."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NamespaceGroup:
    """A logical grouping of variables sharing a common prefix."""

    prefix: str
    vars: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return f"NamespaceGroup(prefix={self.prefix!r}, count={len(self.vars)})"

    def to_dict(self) -> dict:
        return {"prefix": self.prefix, "vars": dict(self.vars)}

    @classmethod
    def from_dict(cls, data: dict) -> "NamespaceGroup":
        return cls(prefix=data["prefix"], vars=dict(data.get("vars", {})))


@dataclass
class NamespaceReport:
    """Result of partitioning variables into namespaces."""

    groups: Dict[str, NamespaceGroup] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    @property
    def group_count(self) -> int:
        return len(self.groups)

    @property
    def ungrouped_count(self) -> int:
        return len(self.ungrouped)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"NamespaceReport(groups={self.group_count}, "
            f"ungrouped={self.ungrouped_count})"
        )


class EnvNamespace:
    """Partition environment variables into namespace groups by prefix."""

    def __init__(self, separator: str = "_") -> None:
        if not separator:
            raise ValueError("separator must be a non-empty string")
        self.separator = separator

    def partition(
        self,
        vars: Dict[str, str],
        prefixes: Optional[List[str]] = None,
    ) -> NamespaceReport:
        """Group *vars* by known *prefixes*; remaining vars go to ungrouped.

        If *prefixes* is None every distinct first-segment is treated as a
        namespace prefix.
        """
        if prefixes is None:
            prefixes = self._discover_prefixes(vars)

        groups: Dict[str, NamespaceGroup] = {}
        ungrouped: Dict[str, str] = {}

        for name, value in vars.items():
            matched = False
            for prefix in prefixes:
                if name.startswith(prefix + self.separator) or name == prefix:
                    if prefix not in groups:
                        groups[prefix] = NamespaceGroup(prefix=prefix)
                    groups[prefix].vars[name] = value
                    matched = True
                    break
            if not matched:
                ungrouped[name] = value

        return NamespaceReport(groups=groups, ungrouped=ungrouped)

    def _discover_prefixes(self, vars: Dict[str, str]) -> List[str]:
        """Return all first-segment prefixes that appear more than once."""
        from collections import Counter

        counts: Counter = Counter()
        for name in vars:
            parts = name.split(self.separator, 1)
            if len(parts) > 1:
                counts[parts[0]] += 1
        return [p for p, c in counts.items() if c > 1]

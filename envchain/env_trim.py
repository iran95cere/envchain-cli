"""Trim whitespace from environment variable names and values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TrimResult:
    """Result of trimming a single variable."""
    name: str
    original_value: str
    trimmed_value: str

    @property
    def changed(self) -> bool:
        return self.original_value != self.trimmed_value

    def __repr__(self) -> str:
        status = "changed" if self.changed else "unchanged"
        return f"TrimResult({self.name!r}, {status})"


@dataclass
class TrimReport:
    """Aggregated report of all trim operations."""
    results: List[TrimResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def changed_vars(self) -> List[TrimResult]:
        return [r for r in self.results if r.changed]

    def to_dict(self) -> dict:
        return {
            "changed_count": self.changed_count,
            "results": [
                {
                    "name": r.name,
                    "original_value": r.original_value,
                    "trimmed_value": r.trimmed_value,
                    "changed": r.changed,
                }
                for r in self.results
            ],
        }


class EnvTrimmer:
    """Trim leading/trailing whitespace from env var values."""

    def trim(self, variables: Dict[str, str]) -> Tuple[Dict[str, str], TrimReport]:
        """Return trimmed variables dict and a report of changes."""
        report = TrimReport()
        trimmed: Dict[str, str] = {}
        for name, value in variables.items():
            tv = value.strip()
            report.results.append(TrimResult(name=name, original_value=value, trimmed_value=tv))
            trimmed[name] = tv
        return trimmed, report

    def trim_names(self, variables: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
        """Return dict with trimmed keys; list of renamed keys."""
        renamed: List[str] = []
        result: Dict[str, str] = {}
        for name, value in variables.items():
            stripped = name.strip()
            if stripped != name:
                renamed.append(name)
            result[stripped] = value
        return result, renamed

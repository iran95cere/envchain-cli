"""Enforce or convert environment variable names to uppercase."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UppercaseResult:
    name: str
    original: str
    converted: str

    @property
    def changed(self) -> bool:
        return self.original != self.converted

    def __repr__(self) -> str:  # pragma: no cover
        tag = "changed" if self.changed else "unchanged"
        return f"<UppercaseResult {self.name!r} {tag}>"


@dataclass
class UppercaseReport:
    results: List[UppercaseResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_dict(self) -> Dict:
        return {
            "changed_count": self.changed_count,
            "results": [
                {"name": r.name, "original": r.original, "converted": r.converted}
                for r in self.results
            ],
        }


class EnvUppercaser:
    """Convert all variable names in a vars dict to uppercase."""

    def convert(self, vars_dict: Dict[str, str]) -> UppercaseReport:
        results: List[UppercaseResult] = []
        for name, value in vars_dict.items():
            converted = name.upper()
            results.append(UppercaseResult(name=name, original=name, converted=converted))
        return UppercaseReport(results=results)

    def apply(self, vars_dict: Dict[str, str], report: UppercaseReport) -> Dict[str, str]:
        """Return a new dict with converted keys from the report."""
        mapping = {r.original: r.converted for r in report.results}
        return {mapping.get(k, k): v for k, v in vars_dict.items()}

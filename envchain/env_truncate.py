"""Truncate long environment variable values to a maximum length."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TruncateResult:
    name: str
    original: str
    truncated: str
    max_length: int

    @property
    def changed(self) -> bool:
        return self.original != self.truncated

    def __repr__(self) -> str:
        status = "truncated" if self.changed else "unchanged"
        return f"<TruncateResult name={self.name!r} status={status}>"


@dataclass
class TruncateReport:
    results: List[TruncateResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_dict(self) -> Dict:
        return {
            "changed_count": self.changed_count,
            "total": len(self.results),
            "results": [
                {
                    "name": r.name,
                    "original_length": len(r.original),
                    "truncated_length": len(r.truncated),
                    "changed": r.changed,
                }
                for r in self.results
            ],
        }


class EnvTruncator:
    """Truncate environment variable values that exceed a maximum length."""

    DEFAULT_MAX_LENGTH = 256
    DEFAULT_SUFFIX = "..."

    def __init__(self, max_length: int = DEFAULT_MAX_LENGTH, suffix: str = DEFAULT_SUFFIX):
        if max_length < len(suffix):
            raise ValueError("max_length must be >= length of suffix")
        self.max_length = max_length
        self.suffix = suffix

    def truncate_value(self, value: str) -> str:
        if len(value) <= self.max_length:
            return value
        cut = self.max_length - len(self.suffix)
        return value[:cut] + self.suffix

    def truncate(self, vars_dict: Dict[str, str]) -> TruncateReport:
        results = []
        for name, original in vars_dict.items():
            truncated = self.truncate_value(original)
            results.append(TruncateResult(
                name=name,
                original=original,
                truncated=truncated,
                max_length=self.max_length,
            ))
        return TruncateReport(results=results)

    def apply(self, vars_dict: Dict[str, str]) -> Dict[str, str]:
        report = self.truncate(vars_dict)
        return {r.name: r.truncated for r in report.results}

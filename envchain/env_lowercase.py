"""Lowercase transformation for environment variable values."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LowercaseResult:
    name: str
    original: str
    transformed: str

    @property
    def changed(self) -> bool:
        return self.original != self.transformed

    def __repr__(self) -> str:  # pragma: no cover
        status = "changed" if self.changed else "unchanged"
        return f"<LowercaseResult name={self.name!r} status={status}>"


@dataclass
class LowercaseReport:
    results: List[LowercaseResult] = field(default_factory=list)

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
                    "original": r.original,
                    "transformed": r.transformed,
                    "changed": r.changed,
                }
                for r in self.results
            ],
        }


class EnvLowercaser:
    """Transforms environment variable values to lowercase."""

    def run(self, vars_: Dict[str, str]) -> LowercaseReport:
        results = []
        for name, value in vars_.items():
            transformed = value.lower()
            results.append(LowercaseResult(name=name, original=value, transformed=transformed))
        return LowercaseReport(results=results)

    def apply(self, vars_: Dict[str, str]) -> Dict[str, str]:
        report = self.run(vars_)
        return {r.name: r.transformed for r in report.results}

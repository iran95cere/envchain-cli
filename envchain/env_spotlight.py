"""Spotlight: highlight and rank env vars by importance heuristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_HIGH_PRIORITY_PATTERNS = (
    "SECRET", "TOKEN", "PASSWORD", "KEY", "API", "AUTH", "PRIVATE", "CERT",
)
_LOW_PRIORITY_PATTERNS = ("DEBUG", "LOG", "VERBOSE", "TRACE", "TEST")


@dataclass
class SpotlightResult:
    name: str
    value: str
    score: int
    reason: str

    def __repr__(self) -> str:
        return f"<SpotlightResult name={self.name!r} score={self.score} reason={self.reason!r}>"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "score": self.score,
            "reason": self.reason,
        }


@dataclass
class SpotlightReport:
    results: List[SpotlightResult] = field(default_factory=list)

    @property
    def high_priority(self) -> List[SpotlightResult]:
        return [r for r in self.results if r.score >= 10]

    @property
    def low_priority(self) -> List[SpotlightResult]:
        return [r for r in self.results if r.score <= 2]

    @property
    def total(self) -> int:
        return len(self.results)

    def top(self, n: int = 5) -> List[SpotlightResult]:
        return sorted(self.results, key=lambda r: r.score, reverse=True)[:n]

    def __repr__(self) -> str:
        return f"<SpotlightReport total={self.total} high={len(self.high_priority)}>"


class EnvSpotlight:
    """Rank environment variables by importance."""

    def analyse(self, vars_: Dict[str, str]) -> SpotlightReport:
        results = []
        for name, value in vars_.items():
            score, reason = self._score(name, value)
            results.append(SpotlightResult(name=name, value=value, score=score, reason=reason))
        return SpotlightReport(results=results)

    def _score(self, name: str, value: str) -> tuple:
        upper = name.upper()
        for pat in _HIGH_PRIORITY_PATTERNS:
            if pat in upper:
                return 10, f"matches high-priority pattern '{pat}'"
        for pat in _LOW_PRIORITY_PATTERNS:
            if pat in upper:
                return 2, f"matches low-priority pattern '{pat}'"
        if len(value) > 64:
            return 7, "long value may contain sensitive data"
        if not value.strip():
            return 1, "empty value"
        return 5, "standard variable"

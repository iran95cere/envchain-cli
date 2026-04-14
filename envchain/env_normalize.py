"""Normalize environment variable names and values across a profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NormalizeResult:
    name: str
    original_value: str
    normalized_value: str

    @property
    def changed(self) -> bool:
        return self.original_value != self.normalized_value

    def __repr__(self) -> str:  # pragma: no cover
        status = "changed" if self.changed else "unchanged"
        return f"<NormalizeResult {self.name!r} {status}>"


@dataclass
class NormalizeReport:
    results: List[NormalizeResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def to_normalized_vars(self) -> Dict[str, str]:
        return {r.name: r.normalized_value for r in self.results}

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NormalizeReport vars={len(self.results)} changed={self.changed_count}>"


class EnvNormalizer:
    """Normalize variable values by applying configurable transformations."""

    STRATEGIES = ("strip", "lower", "upper", "strip_quotes")

    def __init__(self, strategies: Optional[List[str]] = None) -> None:
        self.strategies: List[str] = strategies if strategies is not None else ["strip"]
        for s in self.strategies:
            if s not in self.STRATEGIES:
                raise ValueError(f"Unknown strategy: {s!r}. Choose from {self.STRATEGIES}")

    def _apply(self, value: str) -> str:
        for strategy in self.strategies:
            if strategy == "strip":
                value = value.strip()
            elif strategy == "lower":
                value = value.lower()
            elif strategy == "upper":
                value = value.upper()
            elif strategy == "strip_quotes":
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
        return value

    def normalize(self, vars_dict: Dict[str, str]) -> NormalizeReport:
        results = [
            NormalizeResult(
                name=name,
                original_value=value,
                normalized_value=self._apply(value),
            )
            for name, value in vars_dict.items()
        ]
        return NormalizeReport(results=results)

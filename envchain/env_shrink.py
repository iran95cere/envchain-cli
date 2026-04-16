"""Shrink environment variable values by applying compression strategies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ShrinkResult:
    name: str
    original: str
    shrunk: str
    strategy: str

    @property
    def changed(self) -> bool:
        return self.original != self.shrunk

    @property
    def saved_bytes(self) -> int:
        return len(self.original.encode()) - len(self.shrunk.encode())

    def __repr__(self) -> str:
        status = f"saved {self.saved_bytes}B" if self.changed else "unchanged"
        return f"<ShrinkResult name={self.name!r} strategy={self.strategy!r} {status}>"


@dataclass
class ShrinkReport:
    results: List[ShrinkResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def total_saved_bytes(self) -> int:
        return sum(r.saved_bytes for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def __repr__(self) -> str:
        return (
            f"<ShrinkReport changed={self.changed_count}/{len(self.results)}"
            f" saved={self.total_saved_bytes}B>"
        )


class EnvShrinker:
    """Apply shrink strategies to environment variable values."""

    STRATEGIES = ("strip", "collapse_whitespace", "lowercase_booleans")

    def __init__(self, strategy: str = "strip") -> None:
        if strategy not in self.STRATEGIES:
            raise ValueError(
                f"Unknown strategy {strategy!r}. Choose from {self.STRATEGIES}."
            )
        self.strategy = strategy

    def _apply(self, value: str) -> str:
        if self.strategy == "strip":
            return value.strip()
        if self.strategy == "collapse_whitespace":
            import re
            return re.sub(r"\s+", " ", value).strip()
        if self.strategy == "lowercase_booleans":
            if value.strip().lower() in ("true", "false", "yes", "no"):
                return value.strip().lower()
            return value
        return value

    def shrink(self, vars_: Dict[str, str]) -> ShrinkReport:
        results = [
            ShrinkResult(
                name=k,
                original=v,
                shrunk=self._apply(v),
                strategy=self.strategy,
            )
            for k, v in vars_.items()
        ]
        return ShrinkReport(results=results)

    def to_dict(self, report: ShrinkReport) -> Dict[str, str]:
        return {r.name: r.shrunk for r in report.results}

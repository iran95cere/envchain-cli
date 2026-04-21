"""Squeeze consecutive duplicate values in a profile's env vars."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SqueezeResult:
    name: str
    original: str
    squeezed: str

    @property
    def changed(self) -> bool:
        return self.original != self.squeezed

    def __repr__(self) -> str:  # pragma: no cover
        status = "changed" if self.changed else "unchanged"
        return f"SqueezeResult({self.name!r}, {status})"


@dataclass
class SqueezeReport:
    results: List[SqueezeResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"SqueezeReport(changed={self.changed_count}/{len(self.results)})"


class EnvSqueezer:
    """Remove consecutive repeated characters from env var values."""

    def __init__(self, char: str = " ") -> None:
        if len(char) != 1:
            raise ValueError("char must be a single character")
        self.char = char

    def squeeze_value(self, value: str) -> str:
        """Collapse runs of *char* down to a single occurrence."""
        if not value:
            return value
        result: List[str] = []
        prev = ""
        for ch in value:
            if ch == self.char and ch == prev:
                continue
            result.append(ch)
            prev = ch
        return "".join(result)

    def squeeze(self, vars_: Dict[str, str]) -> SqueezeReport:
        results: List[SqueezeResult] = []
        for name, original in vars_.items():
            squeezed = self.squeeze_value(original)
            results.append(SqueezeResult(name=name, original=original, squeezed=squeezed))
        return SqueezeReport(results=results)

    def apply(self, vars_: Dict[str, str]) -> Tuple[Dict[str, str], SqueezeReport]:
        report = self.squeeze(vars_)
        new_vars = {r.name: r.squeezed for r in report.results}
        return new_vars, report

"""Align environment variable values to a consistent padding/format."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AlignResult:
    name: str
    original: str
    aligned: str

    @property
    def changed(self) -> bool:
        return self.original != self.aligned

    def __repr__(self) -> str:
        status = "changed" if self.changed else "unchanged"
        return f"<AlignResult name={self.name!r} {status}>"


@dataclass
class AlignReport:
    results: List[AlignResult] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.results if r.changed)

    @property
    def has_changes(self) -> bool:
        return self.changed_count > 0

    def aligned_vars(self) -> Dict[str, str]:
        return {r.name: r.aligned for r in self.results}

    def __repr__(self) -> str:
        return f"<AlignReport total={len(self.results)} changed={self.changed_count}>"


class EnvAligner:
    """Align variable values by stripping and optionally padding to a fixed width."""

    def __init__(self, pad_width: int = 0, fill_char: str = " "):
        if pad_width < 0:
            raise ValueError("pad_width must be >= 0")
        self.pad_width = pad_width
        self.fill_char = fill_char

    def align(self, variables: Dict[str, str]) -> AlignReport:
        results = []
        for name, value in variables.items():
            stripped = value.strip()
            if self.pad_width > 0:
                aligned = stripped.ljust(self.pad_width, self.fill_char)
            else:
                aligned = stripped
            results.append(AlignResult(name=name, original=value, aligned=aligned))
        return AlignReport(results=results)
